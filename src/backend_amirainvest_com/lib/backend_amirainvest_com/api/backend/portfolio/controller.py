from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func, label

from backend_amirainvest_com.api.backend.portfolio.model import (
    HistoricalTrade,
    Holding,
    HoldingPercentageRate,
    MarketValue,
    PortfolioValue,
)
from common_amirainvest_com.schemas.schema import (
    FinancialAccountHoldingsHistory,
    FinancialAccounts,
    FinancialAccountTransactions,
    PlaidSecurities,
    Securities,
    SecurityPrices,
    UserSubscriptions,
)
from common_amirainvest_com.utils.decorators import Session


async def get_portfolio_trades(user_id: str, is_creator: bool) -> list[HistoricalTrade]:
    pass
    # trading_history = await get_trading_history(user_id)
    # baseline_holdings = await get_baseline_holdings()
    # response: list[HistoricalTrade] = []
    # percentage_change_in_pos = Decimal(100)
    # for trade in trading_history:
    #     fat = trade.FinancialAccountTransactions
    #     mv = fat.price * fat.quantity
    #     response.append(
    #         HistoricalTrade(
    #             trade_date=fat.posting_date,
    #             ticker=trade.PlaidSecurities.ticker_symbol,
    #             transaction_type=fat.type,
    #             transaction_price=fat.price,
    #             transaction_market_value=is_creator if is_creator else mv,
    #             percentage_change_in_position=percentage_change_in_pos,
    #         )
    #     )
    #
    # return response


async def get_portfolio_holdings(user_id: str, is_creator: bool) -> list[Holding]:
    holdings = await get_user_holdings_with_securities_data(user_id=user_id)
    portfolio = get_portfolio_value(holdings=holdings, user_id=user_id)

    response = []
    for holding in holdings:
        fa = holding.FinancialAccountCurrentHoldings
        ps = holding.PlaidSecurities

        market_value = fa.latest_price * fa.quantity
        response.append(
            Holding(
                ticker=ps.ticker_symbol,
                ticker_price=fa.latest_price,
                ticker_price_time=fa.latest_price_date,
                percentage_of_portfolio=Decimal(market_value / portfolio.value),
                buy_date=holding.buy_date,
                return_percentage=Decimal(fa.cost_basis / fa.quantity),
                market_value=None if is_creator else market_value,
            )
        )
    return response


@Session
async def get_cash_transactions_by_date(
    session: AsyncSession, user_id: int
) -> dict[date, list[FinancialAccountTransactions]]:
    transactions_response = await session.execute(
        select(FinancialAccountTransactions).join(FinancialAccounts).where(FinancialAccounts.user_id == user_id)
    )
    transactions = transactions_response.scalars().all()

    d: dict[date, list[FinancialAccountTransactions]] = {}
    for tx in transactions:
        try:
            d[tx.posting_date.date()].append(tx)
        except KeyError:
            d[tx.posting_date.date()] = [tx]
    return d


@Session
async def get_market_values_for_account(session: AsyncSession, account_id: int) -> list[MarketValue]:
    # TODO validate how we should label market value of short position, can we take the naive approach?
    market_value_by_day_response = await session.execute(
        select(
            FinancialAccountHoldingsHistory.price_time,
            label(
                "market_value",
                func.sum(FinancialAccountHoldingsHistory.price * FinancialAccountHoldingsHistory.quantity),
            ),
        )
        .where(FinancialAccountHoldingsHistory.account_id == account_id)
        .group_by(FinancialAccountHoldingsHistory.price_time)
        .order_by(FinancialAccountHoldingsHistory.price_time.asc())
    )
    results = market_value_by_day_response.all()
    market_values = []
    for res in results:
        d = res._asdict()
        market_values.append(MarketValue(**d))
    return market_values


@Session
async def get_market_values(session: AsyncSession, user_id: int) -> list[MarketValue]:
    # TODO validate how we should label market value of short position, can we take the naive approach?
    market_value_by_day_response = await session.execute(
        select(
            FinancialAccountHoldingsHistory.price_time,
            label(
                "market_value",
                func.sum(FinancialAccountHoldingsHistory.price * FinancialAccountHoldingsHistory.quantity),
            ),
        )
        .join(FinancialAccounts)
        .where(FinancialAccounts.user_id == user_id)
        .group_by(FinancialAccountHoldingsHistory.price_time)
        .order_by(FinancialAccountHoldingsHistory.price_time.asc())
    )

    results = market_value_by_day_response.all()
    market_values = []
    for res in results:
        d = res._asdict()
        market_values.append(MarketValue(**d))
    return market_values


async def get_summary(user_id: str):
    pass
    # market_values = await get_market_values(user_id=user_id)
    # cash_transactions_by_date = await get_cash_transactions_by_date(user_id=user_id)

    # list of portfolio dates and daily returns
    # portfolio_holding_rates = await get_portfolio_holding_percentage_rates(
    #     market_values=market_values, cash_transactions_by_date=cash_transactions_by_date
    # )
    # TODO calculate time weighted return


async def get_portfolio_holding_percentage_rates(
    market_values: list[MarketValue], cash_transactions_by_date: dict[date, list[FinancialAccountTransactions]]
) -> list[HoldingPercentageRate]:
    holding_percentage_rates: list[HoldingPercentageRate] = [
        HoldingPercentageRate(rate=market_values[0].value, date=market_values[0].date)
    ]

    for index, _ in enumerate(market_values[1:]):
        mv_today = market_values[index].value
        mv_today_date = market_values[index].date
        mv_yesterday = holding_percentage_rates[len(holding_percentage_rates) - 1].value
        mv_yesterday_date = holding_percentage_rates[len(holding_percentage_rates) - 1].date

        # Two if statements factor subtract deposits / add back withdraws
        # dividends / interest fees / etc, are already added in via holdings history
        if mv_yesterday_date in cash_transactions_by_date:
            mv_yesterday = modify_market_value_by_cash_flow(
                market_value=mv_yesterday, transactions=cash_transactions_by_date[mv_yesterday_date]
            )

        hpr = (mv_today - mv_yesterday) / mv_today
        holding_percentage_rates.append(HoldingPercentageRate(rate=hpr, date=mv_today_date))

    return holding_percentage_rates


def modify_market_value_by_cash_flow(
    market_value: Decimal, transactions: list[FinancialAccountTransactions]
) -> Decimal:
    # TODO subtract deposits + add back withdraws
    #   to note... dividends/interest fees / etc... are already allocated to cash in the holdings history
    #   we do not need to account for them
    # for tx in transactions:
    #     if tx.type == "cash":
    #         pass
    #     if tx.type == ""
    return market_value


@Session
async def get_user_subscription(session: AsyncSession, user_id: str, creator_id: str) -> Optional[UserSubscriptions]:
    response = await session.execute(
        select(UserSubscriptions)
        .where(UserSubscriptions.subscriber_id == user_id)
        .where(UserSubscriptions.creator_id == creator_id)
    )
    return response.scalar()


@Session
async def get_user_holdings_with_securities_data(session: AsyncSession, user_id: str) -> list:
    response = await session.execute(
        select(FinancialAccountHoldingsHistory, PlaidSecurities)
        .join(PlaidSecurities)
        .join(FinancialAccounts)
        .where(
            FinancialAccounts.user_id == user_id,
            FinancialAccountHoldingsHistory.holding_date
            == select(func.max(FinancialAccountHoldingsHistory.holding_date)),
        )
    )
    return response.all()


@Session
async def get_recent_stock_price(session: AsyncSession, ticker_symbol: str) -> Optional[SecurityPrices]:
    # We want to do a join and get the price of a security by symbol most recent time
    return (
        await session.execute(
            select(SecurityPrices)
            .join(Securities.id)
            .where(Securities.ticker_symbol == ticker_symbol)
            .order_by(SecurityPrices.price_time.desc())
            .limit(1)
        )
    ).scalar()


def compute_buy_date(share_qty: Decimal, transactions: list[FinancialAccountTransactions]) -> tuple:
    buy_date = None
    for tx in transactions:
        if tx.type == "buy":
            share_qty = Decimal(share_qty) + tx.quantity
        if tx.type == "sell":
            share_qty = Decimal(share_qty) - tx.quantity

        if buy_date is None and tx.type == "buy":
            buy_date = tx.posting_date

        if buy_date is not None and tx.type == "buy" and share_qty == 0:
            buy_date = tx.posting_date

    return buy_date, share_qty


@Session
async def get_ticker_symbol_by_plaid_id(session: AsyncSession, plaid_id: int) -> Optional[PlaidSecurities]:
    return (await session.execute(select(PlaidSecurities).where(PlaidSecurities.id == plaid_id))).scalar()


@Session
async def get_trading_history(session: AsyncSession, user_id: str) -> list:
    response = await session.execute(
        select(FinancialAccountTransactions, PlaidSecurities)
        .join(FinancialAccounts)
        .join(PlaidSecurities)
        .where(FinancialAccounts.user_id == user_id)
        .order_by(FinancialAccountTransactions.posting_date.desc())
    )
    return response.all()


def get_portfolio_value(holdings: list, user_id: str) -> PortfolioValue:
    portfolio_value = PortfolioValue(user_id=user_id, value=0)
    for holding in holdings:
        fa = holding.FinancialAccountCurrentHoldings
        value = portfolio_value.value + Decimal(fa.quantity * fa.latest_price)
        portfolio_value.value = value

    return portfolio_value


if __name__ == "__main__":
    pass
