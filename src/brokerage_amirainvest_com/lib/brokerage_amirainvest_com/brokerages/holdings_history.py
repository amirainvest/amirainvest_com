import asyncio
import decimal
from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal
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
    date: date
    user_id: str
    cash: decimal.Decimal
    holdings: list[FinancialAccountHoldingsHistory]


@Session
async def get_prices_all_time(
    session: AsyncSession, plaid_security_ids: set[int], start_time: date, end_time: date
) -> dict[int, list[SecurityPrices]]:
    # TODO Add in a with clause here ot get the max EOD price for all days... rather than just grabbing all prices
    response = await session.execute(
        select(SecurityPrices)
            .join(Securities)
            .join(PlaidSecurities)
            .where(
            PlaidSecurities.id.in_(plaid_security_ids),
            SecurityPrices.price_time <= start_time,
            SecurityPrices.price_time >= end_time,
        )
            .order_by(SecurityPrices.price_time.desc())
    )

    security_prices = response.scalars().all()
    prices: dict[int, list[SecurityPrices]] = {}
    for sp in security_prices:
        try:
            prices[sp.security_id].append(sp)
        except KeyError:
            prices[sp.security_id] = [sp]

    # Order
    for p in prices:
        sp = prices[p]
        sp.sort(key=lambda x: x.price_time, reverse=True)
        prices[p] = sp
    return prices


async def compute_account_holdings_history(
    transactions_by_date: dict[date, list[FinancialAccountTransactions]],
    account: FinancialAccounts,
    user_id: str,
    holdings: list[FinancialAccountCurrentHoldings],
    market_dates: list[date],
    plaid_cash_security: PlaidSecurities,
    prices_all_time: dict[int, list[SecurityPrices]]
) -> list[HistoricalAccount]:
    # Compute array of trading days and then iterate over that... rather than doing it per day and trying to
    # fix the next day, we can always just reference one back
    # [[Holdings]]; first security is always cash hen we only have one data structure to keep in head...
    historical_account = await create_historical_account(
        holdings=holdings,
        account=account,
        user_id=user_id,
        cash_security=plaid_cash_security,
        trading_day=market_dates[0],
    )

    account_historical_holdings: list = [historical_account]

    idx = 0
    while idx < len(market_dates) - 1:
        market_date = market_dates[idx]
        holdings_today = deepcopy(account_historical_holdings[len(account_historical_holdings) - 1])
        if market_date in transactions_by_date:
            transactions = transactions_by_date[market_date]
            # Change this to undo_transactions and loop over them within the function
            holdings_today = await undo_transactions(holdings_today, transactions)

        # Get "yesterdays" market-date, the day before today(2022-01-15 -> 2022-01-14)
        prior_market_day = market_dates[idx + 1]
        prior_holdings = HistoricalAccount(
            id=holdings_today.id,
            date=prior_market_day,
            user_id=holdings_today.user_id,
            holdings=[],
            cash=holdings_today.cash,
        )

        for today_holding in holdings_today.holdings:
            p = today_holding.price
            sp = get_closest_price(prices_all_time, today_holding.security_id, prior_market_day)
            if sp is not None:
                p = sp
            else:
                print("\n\n NO FOUND!!!!!! \n ", today_holding.security_id, ":", prior_market_day)
            today_holding.price = p
            today_holding.holding_date = prior_market_day
            prior_holdings.holdings.append(today_holding)
        account_historical_holdings.append(prior_holdings)
        idx = idx + 1
    account_historical_holdings.sort(key=lambda x: x.date)
    return account_historical_holdings


async def run(user_id: str, start_date: date, end_date: date):
    accounts = await get_financial_accounts(user_id=user_id)
    plaid_cash_security = await get_cash_security_plaid()
    market_dates = await get_market_dates(start_date=start_date, end_date=end_date)
    for account in accounts:
        transactions_by_date = await get_financial_transactions_dict(account_id=account.id)

        holdings = await get_current_financial_holdings(account_id=account.id)

        plaid_security_ids = set()
        for d in transactions_by_date:
            for t in transactions_by_date[d]:
                plaid_security_ids.add(t.plaid_security_id)
        for h in holdings:
            plaid_security_ids.add(h.plaid_security_id)

        prices_all_time = await get_prices_all_time(
            plaid_security_ids=plaid_security_ids, start_time=start_date, end_time=end_date
        )

        account_historical_holdings = await compute_account_holdings_history(
            transactions_by_date=transactions_by_date,
            holdings=holdings,
            market_dates=market_dates,
            plaid_cash_security=plaid_cash_security,
            user_id=user_id,
            account=account,
            prices_all_time=prices_all_time
        )

        await add_holdings_to_database(
            end_date=end_date, historical_holdings=account_historical_holdings, plaid_cash_security=plaid_cash_security
        )


async def add_holdings_to_database(
    end_date: date, historical_holdings: list[HistoricalAccount], plaid_cash_security: PlaidSecurities
):
    insertable = []
    buy_date_dict: dict[int, date] = {}
    cost_basis_dict: dict[int, Decimal] = {}
    for historical_account_holding in historical_holdings:
        cash_holding = FinancialAccountHoldingsHistory(
            account_id=historical_account_holding.id,
            plaid_security_id=plaid_cash_security.id,
            security_id=plaid_cash_security.security_id,
            price=Decimal(1),
            holding_date=historical_account_holding.date,
            quantity=historical_account_holding.cash,
            buy_date=end_date,
        )

        insertable.append(cash_holding)
        for h in historical_account_holding.holdings:
            try:
                buy_date = buy_date_dict[h.plaid_security_id]
            except KeyError:
                buy_date = historical_account_holding.date

            try:
                cost_basis = cost_basis_dict[h.plaid_security_id]
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


async def get_market_dates(start_date: date, end_date: date) -> list[date]:
    market_holidays = await get_market_holidays_dict()
    market_dates: list[date] = []
    end_date = end_date + relativedelta(days=1)
    while start_date >= end_date:
        start_date = start_date - relativedelta(days=1)
        if not is_trading_day(day=start_date, market_holidays=market_holidays):
            continue
        market_dates.append(start_date)
    market_dates.sort(reverse=True)
    return market_dates


def is_trading_day(day: date, market_holidays: dict[date, None]) -> bool:
    if day in market_holidays or day.weekday() > 4:
        return False
    return True


async def create_historical_account(
    holdings: list[FinancialAccountCurrentHoldings],
    account: FinancialAccounts,
    user_id: str,
    cash_security: PlaidSecurities,
    trading_day: date,
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
        sec_id = await get_security_id_by_plaid_security_id(transaction.plaid_security_id)
        account_holdings.holdings.append(
            FinancialAccountHoldingsHistory(
                account_id=account_holdings.id,
                plaid_security_id=transaction.plaid_security_id,
                security_id=sec_id,
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


async def undo_transactions(
    account_holdings: HistoricalAccount, transactions: list[FinancialAccountTransactions]
) -> HistoricalAccount:
    for transaction in transactions:
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


def get_closest_price(
    prices_all_time: dict[int, list[SecurityPrices]], security_id: int, posting_date: date
) -> Optional[Decimal]:
    try:
        security_prices = prices_all_time[security_id]
        for sp in security_prices:
            if sp.price_time.date() <= posting_date:
                return sp.price
    except KeyError:
        print("\n\n\n SECURITY DOES NOT EXIST!!!!!!!  \n\n\n")
        return None
    return None


@Session
async def get_security_id_by_plaid_security_id(
    session: AsyncSession, plaid_security_id: Optional[int]
) -> Optional[int]:
    if plaid_security_id is None:
        return None
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
    for tx in response.scalars().all():
        try:
            transaction_history_day_dict[tx.posting_date.date()].append(tx)
        except KeyError:
            transaction_history_day_dict[tx.posting_date.date()] = [tx]
    return transaction_history_day_dict


@Session
async def get_current_financial_holdings(
    session: AsyncSession, account_id: int
) -> list[FinancialAccountCurrentHoldings]:
    response = await session.execute(
        select(FinancialAccountCurrentHoldings).where(FinancialAccountCurrentHoldings.account_id == account_id)
    )
    return response.scalars().all()


@Session
async def get_financial_accounts(session: AsyncSession, user_id: str) -> list[FinancialAccounts]:
    response = await session.execute(select(FinancialAccounts).where(FinancialAccounts.user_id == user_id))
    return response.scalars().all()


if __name__ == "__main__":
    ending_date = datetime.utcnow() - relativedelta(years=2)
    starting_date = datetime.now().replace(hour=21, minute=0, second=0, microsecond=0) - relativedelta(days=1)
    asyncio.run(
        run(
            user_id="c014c73b-a589-4752-8465-e0980edc2c4b", start_date=starting_date.date(), end_date=ending_date.date()
        )
    )
