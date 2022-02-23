import asyncio
import csv
from decimal import Decimal

import pytz
from dateutil import parser
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import (
    FinancialAccountCurrentHoldings,
    FinancialAccounts,
    FinancialAccountTransactions,
    PlaidItems,
    PlaidSecurities,
    Securities,
    SecurityPrices,
    Users,
)
from common_amirainvest_com.utils.decorators import Session


ACCOUNTS_FILE = "test_accounts.csv"
PLAID_SECURITIES_FILE = "test_plaid_securities.csv"
SECURITIES_FILE = "test_securities.csv"
SECURITY_PRICES_FILE = "test_securities_prices.csv"
HOLDINGS_FILE = "test_holdings.csv"
TRANSACTION_HISTORY_FILE = "test_transactions.csv"


# Read in accounts
async def get_from_file(file: str):
    with open(file) as f:
        reader = csv.DictReader(f)
        response = []
        for row in reader:
            response.append(row)
        return response


@Session
async def add_user(session: AsyncSession) -> Row:
    user = {
        "email": "test@test.com",
        "username": "test",
        "sub": "1234",
        "first_name": "test",
        "last_name": "test",
        "picture_url": "t",
        "email_verified": True,
    }
    response = (await session.execute(select(Users).where(Users.email == "test@test.com"))).scalar()
    if response is not None:
        return response
    return (await session.execute(insert(Users).values(**user).returning(Users))).one()


@Session
async def add_plaid_account(session: AsyncSession, account: dict) -> Row:
    response = (await session.execute(select(FinancialAccounts).where(FinancialAccounts.id == account["id"]))).scalar()
    if response is not None:
        return response
    return (await session.execute(insert(FinancialAccounts).values(**account).returning(FinancialAccounts))).one()


@Session
async def add_plaid_item(session: AsyncSession, user_id: str) -> Row:
    plaid_item = {"user_id": user_id, "plaid_item_id": "1", "institution_id": None}
    response = (await session.execute(select(PlaidSecurities).where(PlaidItems.user_id == user_id))).scalar()
    if response is not None:
        return response
    return (await session.execute(insert(PlaidItems).values(**plaid_item).returning(PlaidItems))).one()


@Session
async def add_in_groups(session: AsyncSession, tt, items: list):
    group = []
    for item in items:
        group.append(item)
        if len(group) == 1000:
            await session.execute(insert(tt).values(group).on_conflict_do_nothing())
            await session.commit()
            group = []
    await session.execute(insert(tt).values(group).on_conflict_do_nothing())
    await session.commit()


async def bootstrap():
    accounts = await get_from_file(ACCOUNTS_FILE)
    holdings = await get_from_file(HOLDINGS_FILE)
    transactions = await get_from_file(TRANSACTION_HISTORY_FILE)
    securities = await get_from_file(SECURITIES_FILE)
    plaid_securities = await get_from_file(PLAID_SECURITIES_FILE)
    securities_prices = await get_from_file(SECURITY_PRICES_FILE)

    # Add Securities
    for sec in securities:
        sec["id"] = int(sec["id"])
        sec["collect"] = False
        sec["is_benchmark"] = False
        sec["close_price"] = Decimal(sec["close_price"])
        sec["open_price"] = Decimal(sec["open_price"])
        sec["primary_sic_code"] = int(sec["primary_sic_code"]) if sec["primary_sic_code"] != "" else None
        del sec["created_at"]
        del sec["last_updated"]
        del sec["founding_date"]
        del sec["employee_count"]
        del sec["human_readable_name"]
        del sec["address"]
        del sec["ceo"]
        del sec["description"]
        del sec["exchange"]
        del sec["industry"]
        del sec["asset_type"]
        del sec["website"]
        del sec["sector"]
        del sec["phone"]
        del sec["type"]
        del sec["issue_type"]
        del sec["currency"]
    await add_in_groups(Securities, securities)

    et_tz = pytz.timezone("US/Eastern")
    # Add Security Prices
    for sec_p in securities_prices:
        sec_p["id"] = int(sec_p["id"])
        sec_p["security_id"] = int(sec_p["security_id"])
        sec_p["price"] = Decimal(sec_p["price"])
        pt = parser.parse(sec_p["price_time"], ignoretz=True)
        pt = et_tz.localize(pt)
        pt = pt.astimezone(pytz.utc)
        pt = pt.replace(hour=21, minute=0, second=0, microsecond=0, tzinfo=None)
        sec_p["price_time"] = pt
        del sec_p["created_at"]
    await add_in_groups(SecurityPrices, securities_prices)

    # Add PlaidSecurities
    for ps in plaid_securities:
        ps["id"] = int(ps["id"])
        ps["financial_institution_id"] = None
        ps["security_id"] = int(ps["security_id"])
        if ps["is_cash_equivalent"] == "FALSE":
            ps["is_cash_equivalent"] = False
        else:
            ps["is_cash_equivalent"] = True
    await add_in_groups(PlaidSecurities, plaid_securities)

    # Add User
    user = await add_user()

    # Add Plaid Item
    plaid_item = await add_plaid_item(user_id=user.id)

    # # Add Brokerage Account(s)
    account = accounts[0]
    account["id"] = int(account["id"])
    account["user_id"] = user.id
    account["available_to_withdraw"] = None
    account["current_funds"] = Decimal(account["current_funds"])
    account["limit"] = None
    account["plaid_item_id"] = plaid_item.id
    await add_plaid_account(account=account)

    # Add Transactions
    for tx in transactions:
        tx["id"] = int(tx["id"])
        tx["account_id"] = int(tx["account_id"])
        tx["plaid_security_id"] = int(tx["plaid_security_id"])
        pd = parser.parse(tx["posting_date"], ignoretz=True)
        pd = et_tz.localize(pd)
        pd = pd.astimezone(pytz.utc)
        pd = pd.replace(hour=21, minute=0, second=0, microsecond=0, tzinfo=None)
        tx["posting_date"] = pd
        tx["price"] = Decimal(tx["price"])
        tx["quantity"] = Decimal(tx["quantity"])
        tx["value_amount"] = Decimal(tx["value_amount"])
        tx["fees"] = Decimal(tx["fees"])
    await add_in_groups(FinancialAccountTransactions, transactions)

    # Add Holdings
    for h in holdings:
        h["id"] = int(h["id"])
        h["account_id"] = int(h["account_id"])
        h["plaid_security_id"] = int(h["plaid_security_id"])
        h["institution_value"] = Decimal(h["institution_value"])
        h["latest_price"] = Decimal(h["latest_price"])
        h["quantity"] = Decimal(h["quantity"])
        h["cost_basis"] = Decimal(h["cost_basis"]) if h["cost_basis"] != "" else None
        lpd = parser.parse(h["latest_price_date"], ignoretz=True)
        lpd = et_tz.localize(lpd)
        lpd = lpd.astimezone(pytz.utc)
        lpd = lpd.replace(hour=21, minute=0, second=0, microsecond=0, tzinfo=None)
        h["latest_price_date"] = lpd
    await add_in_groups(FinancialAccountCurrentHoldings, holdings)


async def run():
    await bootstrap()


if __name__ == "__main__":
    asyncio.run(run())
