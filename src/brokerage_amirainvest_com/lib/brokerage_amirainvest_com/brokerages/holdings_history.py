import asyncio
import decimal
from copy import deepcopy
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


class HistoricalAccount(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    id: int
    date: datetime
    user_id: str
    cash: decimal.Decimal
    holdings: list[FinancialAccountHoldingsHistory]


async def run(user_id: str):
    accounts = await get_financial_accounts(user_id=user_id)
    market_holidays = await get_market_holidays_dict()
    plaid_cash_security = await get_cash_security_plaid()

    # Run For History
    # end_date = datetime.now().replace(hour=21, minute=0, second=0, microsecond=0) - relativedelta(years=2)
    end_date = datetime.utcnow().replace(month=1, day=1, hour=21, minute=0, second=0, microsecond=0)
    today = datetime.now().replace(hour=21, minute=0, second=0, microsecond=0) + relativedelta(days=1)

    for account in accounts:
        transactions_by_date = await get_financial_transactions_dict(account_id=account.id)
        holdings = await get_current_financial_holdings(account_id=account.id)

        # Need to find today or prior day trading day, and set our holdings that price
        next_trading_day = find_next_trading_day(
            day=datetime.now().replace(hour=21, minute=0, second=0, microsecond=0), market_holidays=market_holidays
        )

        historical_account = await create_historical_account(
            holdings=holdings,
            account=account,
            user_id=user_id,
            cash_security=plaid_cash_security,
            trading_day=next_trading_day,
        )

        historical_account_holdings: list = [historical_account]
        while today > end_date:
            today = today - relativedelta(days=1)
            if not is_trading_day(day=today, market_holidays=market_holidays):
                continue

            today_holdings = deepcopy(historical_account_holdings[len(historical_account_holdings) - 1])

            if today.date() in transactions_by_date:
                transactions = transactions_by_date[today.date()]
                for transaction in transactions:
                    today_holdings = await perform_transaction(today_holdings, transaction)

            tomorrow = find_next_trading_day(today - relativedelta(days=1), market_holidays)
            tomorrow_holdings = HistoricalAccount(
                id=today_holdings.id,
                date=tomorrow,
                user_id=today_holdings.user_id,
                holdings=[],
                cash=today_holdings.cash,
            )

            for today_holding in today_holdings.holdings:
                p = today_holding.price
                sp = await get_closest_price(today_holding.security_id, tomorrow)
                if sp is not None:
                    p = sp.price
                today_holding.price = p
                today_holding.holding_date = tomorrow
                tomorrow_holdings.holdings.append(today_holding)

            historical_account_holdings.append(tomorrow_holdings)

        historical_account_holdings.reverse()
        await add_holdings_to_database(
            end_date=end_date,
            historical_holdings=historical_account_holdings,
            plaid_cash_security=plaid_cash_security
        )


async def add_holdings_to_database(
    end_date: datetime, historical_holdings: list[FinancialAccountHoldingsHistory], plaid_cash_security: PlaidSecurities
):
    insertable = []
    buy_date_dict: [int, date] = {}
    cost_basis_dict: [int, decimal.Decimal] = {}
    for historical_account_holding in historical_holdings:
        cash_holding = FinancialAccountHoldingsHistory(
            account_id=historical_account_holding.id,
            plaid_security_id=plaid_cash_security.id,
            security_id=plaid_cash_security.security_id,
            price=1,
            holding_date=historical_account_holding.date,
            quantity=historical_account_holding.cash,
            buy_date=end_date,
            date=datetime.utcnow()
        )

        insertable.append(cash_holding)
        for h in historical_account_holding.holdings:
            h.date = datetime.utcnow()
            try:
                buy_date = buy_date_dict[h.plaid_security_id]
            except KeyError:
                buy_date = historical_account_holding.date

            try:
                cost_basis = buy_date_dict[h.plaid_security_id]
            except KeyError:
                cost_basis = h.price

            if h.quantity == 0:
                try:
                    del buy_date_dict[h.plaid_security_id]
                except KeyError:
                    pass
                try:
                    del cost_basis_dict[h.plaid_security_id]
                except KeyError:
                    pass
                continue

            h.buy_date = buy_date
            h.cost_basis = cost_basis
            insertable.append(h)
    await insert_historical_holdings(insertable)


def find_next_trading_day(day: datetime, market_holidays: dict[date, None]) -> datetime:
    while not is_trading_day(day, market_holidays):
        day = day - relativedelta(days=1)
    return day


def is_trading_day(day: date, market_holidays: dict[date, None]) -> bool:
    if day in market_holidays or day.weekday() > 4:
        return False
    return True


async def create_historical_account(
    holdings: list[FinancialAccountCurrentHoldings],
    account: FinancialAccounts,
    user_id: str,
    cash_security: PlaidSecurities,
    trading_day: datetime,
) -> HistoricalAccount:
    historical_account = HistoricalAccount(id=account.id, date=trading_day, user_id=user_id, holdings=[], cash=0)

    for holding in holdings:
        security_id = await get_security_id_by_plaid_security_id(holding.plaid_security_id)

        if holding.plaid_security_id == cash_security.id:
            historical_account.cash = holding.quantity
            continue

        historical_account.holdings.append(
            FinancialAccountHoldingsHistory(
                account_id=holding.account_id,
                plaid_security_id=holding.plaid_security_id,
                security_id=security_id,
                quantity=holding.quantity,
                price=holding.latest_price,
                holding_date=trading_day,
            )
        )

    return historical_account


async def buy_buy(account_holdings: HistoricalAccount, transaction: FinancialAccountTransactions) -> HistoricalAccount:
    account_holdings.cash = account_holdings.cash + transaction.value_amount
    current_holding, index = get_current_holding_if_exists(transaction=transaction, holdings=account_holdings.holdings)

    if current_holding is None or index is None:
        raise Exception(
            "How did this buy transactions happen without our holdings having a position, or seeing a sell?"
        )

    current_holding.quantity = current_holding.quantity + (-1 * transaction.quantity)
    account_holdings.holdings[index] = current_holding
    return account_holdings


async def buy_buy_cover(
    account_holdings: HistoricalAccount, transaction: FinancialAccountTransactions
) -> HistoricalAccount:
    account_holdings.cash = account_holdings.cash + transaction.value_amount
    current_holding, index = get_current_holding_if_exists(transaction=transaction, holdings=account_holdings.holdings)

    if current_holding is None or index is None:
        raise Exception("how did this buy to cover happen without a current holdings?")

    if current_holding is not None and index is not None:
        current_holding.quantity = current_holding.quantity + (-1 * transaction.quantity)
        account_holdings.holdings[index] = current_holding

    return account_holdings


async def sell_sell(
    account_holdings: HistoricalAccount, transaction: FinancialAccountTransactions
) -> HistoricalAccount:
    account_holdings.cash = account_holdings.cash + transaction.value_amount
    current_holding, index = get_current_holding_if_exists(transaction=transaction, holdings=account_holdings.holdings)
    if current_holding is None:
        sec_id = await get_security_id_by_plaid_security_id(transaction.security_id)
        account_holdings.holdings.append(
            FinancialAccountHoldingsHistory(
                account_id=account_holdings.id,
                plaid_security_id=transaction.security_id,
                security_id=sec_id,
                user_id=account_holdings.user_id,
                price=transaction.price,
                holding_date=None,
                quantity=(-1 * transaction.quantity),
            )
        )
    elif index is not None:
        current_holding.quantity = current_holding.quantity + (-1 * transaction.quantity)
        current_holding.price = transaction.price
        account_holdings.holdings[index] = current_holding
    else:
        raise Exception(" how did this happen... ")
    return account_holdings


async def sell_sell_short(
    account_holdings: HistoricalAccount, transaction: FinancialAccountTransactions
) -> HistoricalAccount:
    account_holdings.cash = account_holdings.cash + transaction.value_amount
    current_holding, index = get_current_holding_if_exists(transaction=transaction, holdings=account_holdings.holdings)
    if current_holding is None:
        raise Exception("How did this happen??")

    if index is None:
        raise Exception("how did this happen")

    current_holding.quantity = current_holding.quantity + (-1 * transaction.quantity)
    current_holding.price = transaction.price
    account_holdings.holdings[index] = current_holding
    return account_holdings


rule_set = {
    "buy": {"buy": buy_buy},
    "sell": {"sell": sell_sell},
    "short": {"short": sell_sell_short},
    "cover": {"cover": buy_buy_cover},
}


async def perform_transaction(
    account_holdings: HistoricalAccount, transaction: FinancialAccountTransactions
) -> HistoricalAccount:
    try:
        account_holdings = await rule_set[transaction.type][transaction.subtype](account_holdings, transaction)
    except KeyError:
        raise Exception(".... we didnt check for this key ....")  # TODO error message...
    return account_holdings


def get_current_holding_if_exists(
    transaction: FinancialAccountTransactions, holdings: list[FinancialAccountHoldingsHistory]
) -> Tuple[Optional[FinancialAccountHoldingsHistory], Optional[int]]:
    for idx, holding in enumerate(holdings):
        if transaction.plaid_security_id == holding.plaid_security_id and transaction.type:
            return holding, idx
    return None, None


@Session
async def insert_historical_holdings(session: AsyncSession, historical_holdings: list[FinancialAccountHoldingsHistory]):
    session.add_all(historical_holdings)


@Session
async def get_cash_security_plaid(session: AsyncSession) -> Optional[PlaidSecurities]:
    response = await session.execute(select(PlaidSecurities).where(PlaidSecurities.ticker_symbol == "CUR:USD"))
    return response.scalar()


@Session
async def get_closest_price(
    session: AsyncSession, security_id: int, posting_date: datetime
) -> Optional[SecurityPrices]:
    response = await session.execute(
        select(SecurityPrices)
            .join(Securities)
            .where(Securities.id == security_id, SecurityPrices.price_time <= posting_date)
            .order_by(SecurityPrices.price_time.desc())
            .limit(1)
    )
    return response.scalar()


@Session
async def get_security_id_by_plaid_security_id(session: AsyncSession, plaid_security_id: int) -> Optional[int]:
    plaid_response = await session.execute(select(PlaidSecurities).where(PlaidSecurities.id == plaid_security_id))
    plaid_security = plaid_response.scalar()
    if plaid_security is None:
        return None

    security_response = await session.execute(
        select(Securities).where(Securities.ticker_symbol == plaid_security.ticker_symbol)
    )

    security = security_response.scalar()

    if security is None:
        return None
    return security.id


@Session
async def get_market_holidays_dict(session: AsyncSession) -> dict[date, None]:
    response = await session.execute(select(MarketHolidays))

    holiday_dict: dict[date, None] = {}
    for holiday in response.scalars().all():
        holiday_dict[holiday.date] = None
    return holiday_dict


@Session
async def get_financial_transactions_dict(
    session: AsyncSession, account_id: str
) -> dict[date, list[FinancialAccountTransactions]]:
    response = await session.execute(
        select(FinancialAccountTransactions).where(FinancialAccountTransactions.account_id == account_id)
    )

    transaction_history_day_dict: dict[date, list[FinancialAccountTransactions]] = {}
    for item in response.scalars().all():
        try:
            transaction_history_day_dict[item.posting_date.date()].append(item)
        except KeyError:
            transaction_history_day_dict[item.posting_date.date()] = [item]
    return transaction_history_day_dict


@Session
async def get_current_financial_holdings(session: AsyncSession, account_id: int) \
        -> list[FinancialAccountCurrentHoldings]:
    response = await session.execute(
        select(FinancialAccountCurrentHoldings).where(FinancialAccountCurrentHoldings.account_id == account_id)
    )
    return response.scalars().all()


@Session
async def get_financial_accounts(session: AsyncSession, user_id: str) -> list[FinancialAccounts]:
    response = await session.execute(select(FinancialAccounts).where(FinancialAccounts.user_id == user_id))
    return response.scalars().all()


if __name__ == "__main__":
    asyncio.run(run(user_id="53a7c663-2c10-47d1-afbc-bf3962f0dbd0"))
