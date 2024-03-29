from typing import Optional

import plaid  # type: ignore
from fastapi import HTTPException, status
from plaid.api import plaid_api  # type: ignore
from plaid.model.account_base import AccountBase  # type: ignore
from plaid.model.accounts_get_request import AccountsGetRequest  # type: ignore
from plaid.model.item import Item  # type: ignore
from plaid.model.item_get_request import ItemGetRequest  # type: ignore
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.backend.plaid_route.models import CurrentPlaidAccounts, FinancialAccount
from backend_amirainvest_com.controllers.plaid_controller import exchange_public_for_access_token
from common_amirainvest_com.dynamo.models import BrokerageUser
from common_amirainvest_com.dynamo.utils import add_brokerage_user
from common_amirainvest_com.schemas.schema import FinancialAccounts, FinancialInstitutions, PlaidItems
from common_amirainvest_com.sqs.consts import BROKERAGE_DATA_QUEUE_URL
from common_amirainvest_com.sqs.models import Brokerage, BrokerageDataActions, BrokerageDataChange
from common_amirainvest_com.sqs.utils import add_message_to_queue
from common_amirainvest_com.utils.consts import PLAID_CLIENT_ID, PLAID_ENVIRONMENT, PLAID_SECRET
from common_amirainvest_com.utils.decorators import Session


def account_is_in(
    institution_id: Optional[str], name: str, mask: str, accounts: list[AccountBase], new_institution_id: str
) -> bool:
    for account in accounts:
        if account.name == name and account.mask == mask and institution_id == new_institution_id:
            return True
    return False


async def get_plaid_accounts(access_token: str) -> list[AccountBase]:
    plaid_cfg = plaid.Configuration(
        host=PLAID_ENVIRONMENT, api_key={"clientId": PLAID_CLIENT_ID, "secret": PLAID_SECRET}
    )
    client = plaid_api.PlaidApi(plaid.ApiClient(plaid_cfg))
    accounts_request = AccountsGetRequest(access_token=access_token)
    accounts_response = client.accounts_get(accounts_request)
    return accounts_response["accounts"]


async def get_plaid_item(access_token: str) -> Item:
    plaid_cfg = plaid.Configuration(
        host=PLAID_ENVIRONMENT, api_key={"clientId": PLAID_CLIENT_ID, "secret": PLAID_SECRET}
    )
    client = plaid_api.PlaidApi(plaid.ApiClient(plaid_cfg))
    item_request = ItemGetRequest(access_token=access_token)
    items_response = client.item_get(item_request)
    return items_response["item"]


async def confirm_no_duplicates(
    user_id: str, new_accounts: list[AccountBase], new_institution_id: str
) -> tuple[bool, str]:
    # TODO we can make another assumption and check if the institution is an oAuth institution, if it is
    #   we can check the user id and institution id instead of checking each account
    current_accounts = await get_current_accounts(user_id=user_id)
    for ca in current_accounts:
        if account_is_in(ca.plaid_institution_id, ca.account_name, ca.account_mask, new_accounts, new_institution_id):
            return True, ca.item_id
    return False, ""


async def get_and_set_access_token(user_id: str, public_token: str, is_update: bool):
    exchange_response = exchange_public_for_access_token(public_token)
    access_token = exchange_response["access_token"]
    item_id = exchange_response["item_id"]

    new_plaid_accounts = await get_plaid_accounts(access_token=access_token)

    if is_update:
        await add_brokerage_user(BrokerageUser(item_id=item_id, access_token=access_token, user_id=user_id))
        internal_plaid_item = await get_internal_item_id(item_id=item_id)
        await add_plaid_accounts(accounts=new_plaid_accounts, item_id=internal_plaid_item.id)
        return

    new_plaid_item = await get_plaid_item(access_token=access_token)
    dup, old_item_id = await confirm_no_duplicates(
        user_id=user_id, new_accounts=new_plaid_accounts, new_institution_id=new_plaid_item.institution_id
    )

    if dup:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "item_id": old_item_id,
                "message": "Financial login already exists. Re-request in update mode with item_id.",
            },
        )

    institution = await get_institution(new_plaid_item.institution_id)
    await add_brokerage_user(BrokerageUser(item_id=item_id, access_token=access_token, user_id=user_id))
    new_internal_item_id = await add_plaid_item(user_id=user_id, item_id=item_id, institution_id=institution.id)
    await add_plaid_accounts(accounts=new_plaid_accounts, user_id=user_id, internal_item_id=new_internal_item_id)

    add_message_to_queue(
        BROKERAGE_DATA_QUEUE_URL,
        BrokerageDataChange(
            brokerage=Brokerage.plaid,
            user_id=user_id,
            token_identifier=item_id,
            action=BrokerageDataActions.upsert_brokerage_account,
        ),
    )


@Session
async def get_institution(session: AsyncSession, plaid_institution_id: str) -> FinancialInstitutions:
    return (
        (
            await session.execute(
                select(FinancialInstitutions).where(FinancialInstitutions.plaid_id == plaid_institution_id)
            )
        )
        .scalars()
        .one()
    )


@Session
async def get_internal_item_id(session: AsyncSession, item_id: str) -> PlaidItems:
    return (await session.execute(select(PlaidItems).where(PlaidItems.plaid_item_id == item_id))).scalars().one()


@Session
async def add_plaid_accounts(session: AsyncSession, accounts: list[AccountBase], user_id: str, internal_item_id: int):
    inserts = []
    for acc in accounts:
        inserts.append(
            {
                "user_id": user_id,
                "plaid_item_id": internal_item_id,
                "plaid_id": acc.account_id,
                "available_to_withdraw": acc.balances.available,
                "current_funds": acc.balances.current,
                "iso_currency_code": acc.balances.iso_currency_code,
                "limit": acc.balances.limit,
                "mask": acc.mask,
                "official_account_name": acc.official_name,
                "user_assigned_account_name": acc.name,
                "sub_type": str(acc.subtype.value),
                "type": str(acc.type.value),
                "unofficial_currency_code": acc.balances.unofficial_currency_code,
            }
        )
    await session.execute(insert(FinancialAccounts).values(inserts).on_conflict_do_nothing())


@Session
async def add_plaid_item(session: AsyncSession, user_id: str, item_id: str, institution_id: int) -> PlaidItems:
    response = await session.execute(
        insert(PlaidItems)
        .values({"user_id": user_id, "plaid_item_id": item_id, "institution_id": institution_id})
        .on_conflict_do_nothing()
        .returning(PlaidItems)
    )
    return response.scalars().one()


@Session
async def get_current_accounts(session: AsyncSession, user_id: str) -> list[CurrentPlaidAccounts]:
    response = await session.execute(
        select(FinancialAccounts, PlaidItems, FinancialInstitutions)
        .join(FinancialAccounts, isouter=True)
        .join(FinancialInstitutions)
        .where(PlaidItems.user_id == user_id)
        .order_by(PlaidItems.plaid_item_id)
    )

    records = response.all()
    if records is None:
        return []

    cur_accounts: list[CurrentPlaidAccounts] = []
    for record in records:
        plaid_item: PlaidItems = record.PlaidItems
        account: FinancialAccounts = record.FinancialAccounts
        institution: FinancialInstitutions = record.FinancialInstitutions
        if plaid_item is None or account is None:
            continue

        cur_accounts.append(
            CurrentPlaidAccounts(
                item_id=plaid_item.plaid_item_id,
                plaid_institution_id=institution.plaid_id,
                account_name=account.user_assigned_account_name,
                account_mask=account.mask,
            )
        )
    return cur_accounts


@Session
async def get_financial_accounts(session: AsyncSession, user_id: str) -> list[FinancialAccount]:
    response = await session.execute(
        select(FinancialAccounts, FinancialInstitutions, PlaidItems)
        .join(PlaidItems, PlaidItems.id == FinancialAccounts.plaid_item_id)
        .join(FinancialInstitutions, FinancialInstitutions.id == PlaidItems.institution_id)
        .where(FinancialAccounts.user_id == user_id)
    )

    records = response.all()
    if records is None:
        return []

    fin_accounts: list[FinancialAccount] = []
    for record in records:
        account = record.FinancialAccounts
        institution = record.FinancialInstitutions
        item = record.PlaidItems
        fin_accounts.append(
            FinancialAccount(
                item_id=item.plaid_item_id,
                institution_name=institution.name,
                account_name=account.user_assigned_account_name,
                status=account.status.value,
                account_type=account.type,
                account_sub_type=account.sub_type,
            )
        )

    return fin_accounts
