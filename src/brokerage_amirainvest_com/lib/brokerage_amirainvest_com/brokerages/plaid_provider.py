import time
import uuid
from decimal import Decimal

import arrow
import plaid  # type: ignore
from plaid.api import plaid_api  # type: ignore
from plaid.model.account_base import AccountBase as PlaidAccount  # type: ignore
from plaid.model.country_code import CountryCode  # type: ignore
from plaid.model.holding import Holding as PlaidHolding  # type: ignore
from plaid.model.institutions_get_request import InstitutionsGetRequest  # type: ignore
from plaid.model.investment_transaction import InvestmentTransaction as PlaidInvestmentTransaction  # type: ignore
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest  # type: ignore
from plaid.model.investments_transactions_get_request import InvestmentsTransactionsGetRequest  # type: ignore
from plaid.model.investments_transactions_get_request_options import (  # type: ignore
    InvestmentsTransactionsGetRequestOptions,
)
from plaid.model.security import Security as PlaidSecurity  # type: ignore
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from brokerage_amirainvest_com.brokerages.interfaces import BrokerageInterface, TokenRepositoryInterface
from brokerage_amirainvest_com.models import (
    Account,
    AccountType,
    Holding,
    HoldingInformation,
    Institution,
    InvestmentInformation,
    InvestmentTransaction,
    InvestmentTransactionType,
    Security,
    SecurityType,
)
from common_amirainvest_com.schemas.schema import (
    FinancialAccountCurrentHoldings,
    FinancialAccounts,
    FinancialAccountTransactions,
    FinancialInstitutions,
    Securities,
)
from common_amirainvest_com.utils.decorators import Session  # type: ignore


__all__ = ["PlaidRepository", "PlaidHttp", "PlaidProvider"]


class PlaidRepository:
    def __init__(self):
        pass

    @Session
    async def add_institutions(self, session: AsyncSession, institutions: list[Institution]):
        plaid_institution_ids = set()
        for inst_id in institutions:
            plaid_institution_ids.add(inst_id.plaid_institution_id)

        existing_institutions = await self.get_institutions_by_plaid_ids(plaid_institution_ids)
        existing_institutions_dict = {}
        for exist_inst in existing_institutions:
            existing_institutions_dict[exist_inst.plaid_id] = exist_inst.id

        institutions_to_insert = []
        for inst in institutions:
            if inst.plaid_institution_id not in existing_institutions_dict:
                institutions_to_insert.append(
                    {
                        "name": inst.name,
                        "plaid_id": inst.plaid_institution_id,
                        "third_party_institution_id": inst.plaid_institution_id,
                    }
                )

        if len(institutions_to_insert) == 0:
            return

        await session.execute(insert(FinancialInstitutions).values(institutions_to_insert))

    @Session
    async def get_securities_by_plaid_ids(self, session: AsyncSession, ids: list[str]) -> list[Securities]:
        existing_securities_res = await session.execute(select(Securities).where(Securities.plaid_security_id.in_(ids)))
        return existing_securities_res.scalars().all()

    @Session
    async def add_securities(self, session: AsyncSession, securities: list[Security]):
        plaid_security_ids = set()
        plaid_institution_ids = set()

        for security in securities:
            plaid_institution_ids.add(security.institution_id)
            plaid_security_ids.add(security.security_id)

        existing_securities = await self.get_securities_by_plaid_ids(plaid_security_ids)
        existing_securities_dict: dict[str, None] = {}
        for ex in existing_securities:
            existing_securities_dict[ex.plaid_security_id] = None

        current_institutions = await self.get_institutions_by_plaid_ids(plaid_institution_ids)
        existing_institutions_dict: dict[str, int] = {}
        for inst in current_institutions:
            existing_institutions_dict[inst.plaid_id] = inst.id

        securities_to_insert = []
        for sec in securities:
            if sec.security_id in existing_securities_dict:
                continue

            security_dao = Securities(
                plaid_security_id=sec.security_id,
                name=sec.name,
                ticker_symbol=sec.ticker_symbol,
                isin=sec.ticker_symbol,
                cusip=sec.cusip,
                sedol=sec.sedol,
                plaid_institution_security_id=sec.institution_security_id,
                is_cash_equivalent=sec.is_cash_equivalent,
                type=sec.type.value if sec.type is not None else None,
                iso_currency_code=sec.iso_currency_code,
                unofficial_currency_code=sec.unofficial_currency_code,
            )

            try:
                internal_institution_id = existing_institutions_dict[str(sec.institution_id)]
                security_dao.institution_id = internal_institution_id
            except KeyError:
                security_dao.institution_id = None

            securities_to_insert.append(security_dao)
        session.add_all(securities_to_insert)

    @Session
    async def get_institutions_by_plaid_ids(self, session: AsyncSession, ids: list[str]) -> list[FinancialInstitutions]:
        result = await session.execute(select(FinancialInstitutions).where(FinancialInstitutions.plaid_id.in_(ids)))
        return result.scalars().all()

    @Session
    async def get_accounts_by_plaid_ids(self, session: AsyncSession, ids: list[str]) -> list[FinancialAccounts]:
        result = await session.execute(select(FinancialAccounts).where(FinancialAccounts.plaid_id.in_(ids)))
        return result.scalars().all()

    @Session
    async def add_accounts(self, session: AsyncSession, user_id: uuid.UUID, accounts: list[Account]):
        plaid_account_ids = set()
        for account in accounts:
            plaid_account_ids.add(account.account_id)

        current_accounts = await self.get_accounts_by_plaid_ids(plaid_account_ids)
        plaid_to_internal_id = {}
        for acc in current_accounts:
            plaid_to_internal_id[acc.plaid_id] = acc.id

        accounts_to_insert = []
        for acc in accounts:
            if acc.account_id in plaid_to_internal_id:
                continue
            accounts_to_insert.append(
                FinancialAccounts(
                    user_id=user_id,
                    plaid_id=acc.account_id,
                    official_account_name=acc.official_name,
                    user_assigned_account_name=acc.name,
                    available_to_withdraw=acc.available,
                    current_funds=acc.current,
                    mask=acc.mask,
                    type=acc.type.value,
                    sub_type=acc.subtype,
                    limit=acc.limit,
                    iso_currency_code=acc.iso_currency_code,
                    unofficial_currency_code=acc.unofficial_currency_code,
                )
            )
        session.add_all(accounts_to_insert)

    @Session
    async def get_investment_transactions_by_plaid_id(
        self, session: AsyncSession, ids: list[str]
    ) -> list[FinancialAccountTransactions]:
        result = await session.execute(
            select(FinancialAccountTransactions).where(
                FinancialAccountTransactions.plaid_investment_transaction_id.in_(ids)
            )
        )
        return result.scalars().all()

    @Session
    async def add_investment_transactions(
        self, session: AsyncSession, investment_transactions: list[InvestmentTransaction]
    ):
        plaid_account_ids = set()
        plaid_security_ids = set()
        plaid_investment_ids = set()
        for t in investment_transactions:
            plaid_account_ids.add(t.account_id)
            plaid_security_ids.add(t.security_id)
            plaid_investment_ids.add(t.investment_transaction_id)

        current_accounts = await self.get_accounts_by_plaid_ids(plaid_account_ids)
        current_accounts_dict = {}
        for ca in current_accounts:
            current_accounts_dict[ca.plaid_id] = ca.id

        current_securities = await self.get_securities_by_plaid_ids(plaid_security_ids)
        current_securities_dict = {}
        for ci in current_securities:
            current_securities_dict[ci.plaid_security_id] = ci.id

        current_transactions = await self.get_investment_transactions_by_plaid_id(plaid_investment_ids)
        current_transactions_dict = {}
        for ct in current_transactions:
            current_transactions_dict[ct.plaid_investment_transaction_id] = ct.id

        insertable_investment_transactions = []
        for it in investment_transactions:
            if it.investment_transaction_id in current_transactions_dict:
                continue
            security_id = current_securities_dict[it.security_id]
            account_id = current_accounts_dict[it.account_id]

            dt = None
            if it.date is not None:
                dt = arrow.get(it.date, "YYYY-MM-DD").datetime
                dt = dt.replace(tzinfo=None)
            insertable_investment_transactions.append(
                FinancialAccountTransactions(
                    account_id=account_id,
                    security_id=security_id,
                    type=it.type.value,
                    subtype=it.subtype,
                    plaid_investment_transaction_id=it.investment_transaction_id,
                    posting_date=dt,
                    name=it.name,
                    quantity=it.quantity,
                    value_amount=it.amount,
                    price=it.price,
                    fees=it.fees,
                    iso_currency_code=it.iso_currency_code,
                    unofficial_currency_code=it.unofficial_currency_code,
                )
            )
            session.add_all(insertable_investment_transactions)

    @Session
    async def add_holdings(self, session: AsyncSession, holdings: list[Holding], user_id: uuid.UUID):
        plaid_account_ids = set()
        plaid_security_ids = set()

        for t in holdings:
            plaid_account_ids.add(t.account_id)
            plaid_security_ids.add(t.security_id)

        current_accounts = await self.get_accounts_by_plaid_ids(plaid_account_ids)
        current_accounts_dict = {}
        for ca in current_accounts:
            current_accounts_dict[ca.plaid_id] = ca.id

        current_securities = await self.get_securities_by_plaid_ids(plaid_security_ids)
        current_securities_dict = {}
        for ci in current_securities:
            current_securities_dict[ci.plaid_security_id] = ci.id

        insertable_holdings = []
        for h in holdings:
            security_id = current_securities_dict[h.security_id]
            account_id = current_accounts_dict[h.account_id]

            latest_price_date = None
            if h.institution_price_as_of is not None:
                latest_price_date = arrow.get(h.institution_price_as_of, "YYYY-MM-DD").datetime
                latest_price_date = latest_price_date.replace(tzinfo=None)

            insertable_holdings.append(
                FinancialAccountCurrentHoldings(
                    user_id=user_id,
                    account_id=account_id,
                    security_id=security_id,
                    latest_price=h.institution_price,
                    latest_price_date=latest_price_date,
                    institution_value=h.institution_value,
                    cost_basis=h.cost_basis,
                    quantity=h.quantity,
                    iso_currency_code=h.iso_currency_code,
                    unofficial_currency_code=h.unofficial_currency_code,
                )
            )
        await session.execute(
            delete(FinancialAccountCurrentHoldings).where(FinancialAccountCurrentHoldings.user_id == user_id)
        )
        session.add_all(insertable_holdings)
        await session.commit()
        return


class PlaidHttp:
    token_repository: TokenRepositoryInterface
    client: plaid_api.PlaidApi

    def __init__(self, token_repository: TokenRepositoryInterface, client_id: str, secret: str):
        self.token_repository = token_repository
        plaid_cfg = plaid.Configuration(
            host=plaid.Environment.Sandbox, api_key={"clientId": client_id, "secret": secret}
        )
        self.client = plaid_api.PlaidApi(plaid.ApiClient(plaid_cfg))

    def get_investment_history(
        self,
        user_id: uuid.UUID,
        item_id: str,
        start_date: arrow.Arrow = arrow.get("1995-01-01"),
        end_date: arrow.Arrow = arrow.utcnow(),
        offset: int = 0,
    ) -> InvestmentInformation:
        brokerage_user = self.token_repository.get_key(str(user_id))
        if item_id not in brokerage_user.plaid_access_tokens:
            raise Exception("TODO LATER")
        access_token = brokerage_user.plaid_access_tokens[item_id]

        request = InvestmentsTransactionsGetRequest(
            access_token=access_token,
            start_date=start_date.date(),
            end_date=end_date.date(),
            options=InvestmentsTransactionsGetRequestOptions(offset=offset),
        )

        response = self.client.investments_transactions_get(request)
        investment_transactions: list[InvestmentTransaction] = []
        for it in response["investment_transactions"]:
            investment_transactions.append(plaid_investment_transaction_to_investment_transaction(it))

        securities = {}
        for sec in response["securities"]:
            securities[sec.security_id] = plaid_security_to_security(sec)

        accounts = []
        for account in response["accounts"]:
            accounts.append(plaid_account_to_account(account))

        return InvestmentInformation(
            accounts=accounts,
            securities=securities,
            investment_transactions=investment_transactions,
            total_investment_transactions=response["total_investment_transactions"],
        )

    def get_current_holdings(self, user_id: uuid.UUID, item_id: str):
        brokerage_user = self.token_repository.get_key(str(user_id))
        if item_id not in brokerage_user.plaid_access_tokens:
            raise Exception("TODO LATER")
        access_token = brokerage_user.plaid_access_tokens[item_id]
        response = self.client.investments_holdings_get(
            InvestmentsHoldingsGetRequest(
                access_token=access_token,
            )
        )

        holdings: list[Holding] = []
        for holding in response["holdings"]:
            holdings.append(plaid_holding_to_holding(holding))

        securities = {}
        for sec in response["securities"]:
            securities[sec.security_id] = plaid_security_to_security(sec)

        accounts = []
        for account in response["accounts"]:
            accounts.append(plaid_account_to_account(account))

        return HoldingInformation(accounts=accounts, securities=securities, holdings=holdings)

    def get_institutions(self, offset: int, count=500):
        request = InstitutionsGetRequest(country_codes=[CountryCode("US")], count=count, offset=offset)

        response = self.client.institutions_get(request)
        institutions = response["institutions"]
        institutions_response = []

        for institution in institutions:
            institutions_response.append(
                Institution(
                    total=response["total"],
                    plaid_institution_id=institution["institution_id"],
                    name=institution["name"],
                    oauth=institution["oauth"],
                )
            )

        return institutions_response


class PlaidProvider(BrokerageInterface):
    repository: PlaidRepository
    http_client: PlaidHttp

    def __init__(self, repository: PlaidRepository, http_client: PlaidHttp):
        self.repository = repository
        self.http_client = http_client

    async def collect_investment_history(self, user_id: uuid.UUID, item_id: str):
        investment_history = self.http_client.get_investment_history(user_id=user_id, item_id=item_id)

        await self.repository.add_securities(securities=list(investment_history.securities.values()))
        await self.repository.add_accounts(user_id=user_id, accounts=investment_history.accounts)
        await self.repository.add_investment_transactions(
            investment_transactions=investment_history.investment_transactions
        )

        count = len(investment_history.investment_transactions)
        while count < investment_history.total_investment_transactions:
            investment_history = self.http_client.get_investment_history(user_id=user_id, item_id=item_id, offset=count)
            await self.repository.add_securities(securities=list(investment_history.securities.values()))
            await self.repository.add_accounts(user_id=user_id, accounts=investment_history.accounts)
            await self.repository.add_investment_transactions(
                investment_transactions=investment_history.investment_transactions
            )
            count = count + len(investment_history.investment_transactions)

    async def collect_current_holdings(self, user_id: uuid.UUID, item_id: str):
        holdings_information = self.http_client.get_current_holdings(user_id=user_id, item_id=item_id)

        await self.repository.add_securities(securities=list(holdings_information.securities.values()))
        await self.repository.add_accounts(user_id=user_id, accounts=holdings_information.accounts)
        await self.repository.add_holdings(
            holdings=holdings_information.holdings,
            user_id=user_id,
        )

    async def collect_institutions(self):
        institution_response = self.http_client.get_institutions(offset=0)
        await self.repository.add_institutions(institutions=institution_response)
        if len(institution_response) == 0 or institution_response[0].total <= len(institution_response):
            return

        total = institution_response[0].total
        count = len(institution_response)
        while count < total:
            institution_response = self.http_client.get_institutions(offset=count)
            await self.repository.add_institutions(institutions=institution_response)
            count += len(institution_response)
            time.sleep(5)


def plaid_account_to_account(pa: PlaidAccount) -> Account:
    return Account(
        account_id=pa.account_id,
        mask=pa.mask,
        name=pa.name,
        official_name=pa.official_name,
        type=AccountType(pa.type.value),
        subtype=pa.subtype.value,
        available=None if pa.balances.available is None else Decimal(pa.balances.available),
        current=None if pa.balances.current is None else Decimal(pa.balances.current),
        iso_currency_code=pa.balances.iso_currency_code,
        unofficial_currency_code=pa.balances.unofficial_currency_code,
        limit=None if pa.balances.limit is None else Decimal(pa.balances.limit),
    )


def plaid_security_to_security(sec: PlaidSecurity) -> Security:
    return Security(
        security_id=sec.security_id,
        isin=sec.isin,
        cusip=sec.cusip,
        sedol=sec.sedol,
        institution_security_id=sec.institution_security_id,
        institution_id=sec.institution_id,
        proxy_security_id=sec.proxy_security_id,
        name=sec.name,
        ticker_symbol=sec.ticker_symbol,
        is_cash_equivalent=sec.is_cash_equivalent,
        type=SecurityType(sec.type),
        close_price=None if sec.close_price is None else Decimal(sec.close_price),
        close_price_as_of=sec.close_price_as_of,
        iso_currency_code=sec.iso_currency_code,
        unofficial_currency_code=sec.unofficial_currency_code,
    )


def plaid_investment_transaction_to_investment_transaction(it: PlaidInvestmentTransaction) -> InvestmentTransaction:
    return InvestmentTransaction(
        account_id=it.account_id,
        amount=None if it.amount is None else Decimal(it.amount),
        date=arrow.get(it.date).format("YYYY-MM-DD"),
        investment_transaction_id=it.investment_transaction_id,
        security_id=it.security_id,
        name=it.name,
        quantity=None if it.quantity is None else Decimal(it.quantity),
        price=None if it.price is None else Decimal(it.price),
        fees=None if it.fees is None else Decimal(it.fees),
        type=InvestmentTransactionType(it.type),
        subtype=it.subtype,
        iso_currency_code=it.iso_currency_code,
        unofficial_currency_code=it.unofficial_currency_code,
    )


def plaid_holding_to_holding(h: PlaidHolding) -> Holding:
    return Holding(
        account_id=h.account_id,
        security_id=h.security_id,
        institution_price=None if h.institution_price is None else Decimal(h.institution_price),
        institution_price_as_of=None
        if h.institution_price_as_of is None
        else arrow.get(h.institution_price_as_of).format("YYYY-MM-DD"),
        institution_value=None if h.institution_value is None else Decimal(h.institution_value),
        cost_basis=None if h.cost_basis is None else Decimal(h.cost_basis),
        quantity=None if h.quantity is None else Decimal(h.quantity),
        iso_currency_code=h.iso_currency_code,
        unofficial_currency_code=h.unofficial_currency_code,
    )
