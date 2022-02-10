import asyncio
import decimal
from datetime import date, datetime
from typing import Optional, Tuple

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import (
    FinancialAccountCurrentHoldings,
    FinancialAccountHoldingsHistory,
    FinancialAccounts,
    FinancialAccountTransactions,
    MarketHolidays,
    PlaidSecurities,
    Securities,
    SecurityPrices,
)
from common_amirainvest_com.utils.decorators import Session


class AccountHoldings(BaseModel):
    account_id: int
    cash: decimal.Decimal
    holdings: list[FinancialAccountHoldingsHistory]


async def group_accounts_and_holdings(
    current_holdings: list[FinancialAccountCurrentHoldings],
) -> dict[int, AccountHoldings]:
    current_day: dict[int, AccountHoldings] = {}
    # TODO Should we use updated prices from IEX, or can we just use Plaid since this is the most "recent"
    #  data available?
    # TODO Reconcile accounts that might have depository as cash on hand, rather than individual security records
    for holdings in current_holdings:
        security_id = await get_security_id_by_plaid_security_id(holdings.plaid_security_id)
        fah = FinancialAccountHoldingsHistory(
            account_id=holdings.account_id,
            plaid_security_id=holdings.plaid_security_id,
            security_id=security_id,
            user_id=holdings.user_id,
            price=holdings.latest_price,
            price_time=holdings.latest_price_date,
            quantity=holdings.quantity,
        )
        try:
            current_day[holdings.account_id].holdings.append(fah)
        except KeyError:
            current_day[holdings.account_id].holdings = [fah]
    return current_day


async def run(user_id: str):
    transactions_by_date = await get_ordered_transaction_history_per_day(user_id=user_id)
    current_holdings = await get_current_holdings(user_id=user_id)
    market_holidays = await get_market_holidays()

    # Run For History
    two_years_ago = datetime.now().replace(hour=21, minute=0, second=0, microsecond=0) - relativedelta(years=2)
    today = datetime.now().replace(hour=21, minute=0, second=0, microsecond=0)

    # We are going to keep computing yesterday's holdings based on the holdings & transactions TODAY
    tomorrows_holdings: dict[int, AccountHoldings] = await group_accounts_and_holdings(current_holdings)
    holdings_history: list[dict[int, AccountHoldings]] = [tomorrows_holdings]
    while today >= two_years_ago:
        # Can't have any transactions today
        if today.date() in market_holidays or today.weekday() > 4:
            continue
        holdings_today = holdings_history[len(holdings_history) - 1]

        # Check if we have any transactions for today
        # Make changes to the holidays....
        if today.date() in transactions_by_date:
            transactions = transactions_by_date[today.date()]
            for transaction in transactions:
                if transaction.account_id not in holdings_today:
                    raise Exception("Oh Boy... this shouldnt have happened")
                account_holdings = holdings_today[transaction.account_id]
                account_holdings = perform_transaction(account_holdings, transaction)
                tomorrows_holdings[transaction.account_id] = account_holdings

        # Update all of our securities with tomorrow's pricing
        tomorrow_date = today - relativedelta(days=1)
        holdings_tomorrow: dict[int, AccountHoldings] = {}
        for holdings_today_account_id in holdings_today:
            account = holdings_today[holdings_today_account_id]
            new_holding = []
            for holding in account.holdings:
                if 0 >= holding.quantity:
                    continue
                # TODO Support options contract pricing
                security_price = await get_closest_price(holding.security_id, holdings_today_account_id)
                new_holding.append(
                    FinancialAccountHoldingsHistory(
                        account_id=holding.account_id,
                        plaid_security_id=holding.plaid_security_id,
                        security_id=holding.security_id,
                        user_id=holding.user_id,
                        price=security_price.price,
                        price_time=tomorrow_date,
                        quantity=holding.quantity,
                    )
                )
            account.holdings = new_holding
            tomorrows_holdings[holdings_today_account_id] = account

        holdings_history.append(holdings_tomorrow)
        today = today - relativedelta(days=1)
    # TODO When finished completely, go back through and propagate price-time from the bottom up before
    #   inserting into the db


def perform_transaction(
    account_holdings: AccountHoldings, transaction: FinancialAccountTransactions
) -> AccountHoldings:
    current_holding, index = get_current_holding_if_exists(transaction=transaction, holdings=account_holdings.holdings)
    if current_holding is None or index is None:
        if transaction.type == "buy":
            account_holdings.cash = account_holdings.cash + transaction.value_amount
            return account_holdings
        if transaction.type == "sell":
            account_holdings.cash = account_holdings.cash - transaction.value_amount
            return account_holdings
    else:
        if transaction.type == "buy":
            account_holdings.cash = account_holdings.cash + transaction.value_amount
            current_holding.quantity = current_holding.quantity - transaction.quantity
            account_holdings.holdings[index] = current_holding
            return account_holdings
        if transaction.type == "sell":
            account_holdings.cash = account_holdings.cash - transaction.value_amount
            current_holding.quantity = current_holding.quantity + transaction.quantity
            account_holdings.holdings[index] = current_holding
            return account_holdings
    return account_holdings


def get_current_holding_if_exists(
    transaction: FinancialAccountTransactions, holdings: list[FinancialAccountHoldingsHistory]
) -> Tuple[Optional[FinancialAccountHoldingsHistory], Optional[int]]:
    for idx, holding in enumerate(holdings):
        if transaction.security_id == holding.plaid_security_id:
            return holding, idx
    return None, None


@Session
async def get_closest_price(
    session: AsyncSession, security_id: int, posting_date: datetime
) -> Optional[SecurityPrices]:
    # TODO need to update this so that we look at yesterday EOD pricing, rather than today's price at 3:59
    response = await session.execute(
        select(SecurityPrices)
        .join(Securities)
        .where(Securities.id == security_id, SecurityPrices.price_time < posting_date)
        .order_by(SecurityPrices.price_time.desc())
        .limit(1)
    )
    return response.scalar()


@Session
async def get_security_id_by_plaid_security_id(session: AsyncSession, plaid_security_id: int) -> Optional[int]:
    plaid_response = await session.execute(select(PlaidSecurities).where(PlaidSecurities.id == plaid_security_id))
    plaid_security = plaid_response.one()
    security_response = await session.execute(
        select(Securities).where(Securities.ticker_symbol == plaid_security.ticker_symbol)
    )
    security = security_response.scalar()
    if security is None:
        return None
    return security.id


@Session
async def get_market_holidays(session: AsyncSession) -> dict[MarketHolidays, None]:
    response = await session.execute(select(MarketHolidays))

    holiday_dict: dict[MarketHolidays, None] = {}
    for holiday in response.scalars().all():
        holiday_dict[holiday.date.date()] = None
    return holiday_dict


@Session
async def get_ordered_transaction_history_per_day(
    session: AsyncSession, user_id: str
) -> dict[date, list[FinancialAccountTransactions]]:
    response = await session.execute(
        select(FinancialAccountTransactions)
        .join(FinancialAccounts)
        .where(FinancialAccounts.user_id == user_id)
        .order_by(FinancialAccountTransactions.posting_date.desc())
    )

    transaction_history_day_dict: dict[date, list[FinancialAccountTransactions]] = {}
    for item in response.scalars().all():
        try:
            transaction_history_day_dict[item.posting_date].append(item)
        except KeyError:
            transaction_history_day_dict[item.posting_date.date()] = [item]
    return transaction_history_day_dict


@Session
async def get_current_holdings(session: AsyncSession, user_id: str) -> list[FinancialAccountCurrentHoldings]:
    response = await session.execute(
        select(FinancialAccountCurrentHoldings).where(FinancialAccountCurrentHoldings.user_id == user_id)
    )
    return response.scalars().all()


@Session
async def get_financial_accounts(session: AsyncSession, user_id: str) -> list[FinancialAccounts]:
    response = await session.execute(select(FinancialAccounts).where(FinancialAccounts.user_id == user_id))
    return response.scalars().all()


if __name__ == "__main__":
    asyncio.run(run(user_id="f6b8bdfc-5a9d-11ec-bc23-0242ac1a0002"))
