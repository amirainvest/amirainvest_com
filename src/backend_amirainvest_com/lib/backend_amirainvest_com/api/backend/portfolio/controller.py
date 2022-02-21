from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func, label

from backend_amirainvest_com.api.backend.portfolio.model import (
    HistoricalPeriod,
    HistoricalReturn,
    HistoricalTrade,
    Holding,
    MarketValue,
    PortfolioResponse,
    PortfolioType,
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
    trading_history = await get_trading_history(user_id=user_id)
    baseline_holdings = await get_user_baseline_holdings(user_id=user_id)

    security_holdings_dict: dict[int, tuple[Decimal, Decimal]] = {}
    for bh in baseline_holdings:
        security_holdings_dict[bh.PlaidSecurities.id] = (Decimal(100), bh.FinancialAccountHoldingsHistory.quantity)

    response: list[HistoricalTrade] = []
    for trade in trading_history:
        fat = trade.FinancialAccountTransactions
        mv = fat.price * fat.quantity
        response.append(
            HistoricalTrade(
                trade_date=fat.posting_date,
                ticker=trade.PlaidSecurities.ticker_symbol,
                transaction_type=fat.type,
                transaction_price=fat.price,
                transaction_market_value=is_creator if is_creator else mv,
                percentage_change_in_position=None,  # TODO
            )
        )
    return response


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


async def get_portfolio_summary(user_id: str, is_creator: bool) -> PortfolioResponse:
    market_values = await get_market_values(user_id=user_id)
    cash_transactions_by_date = await get_cash_transactions_by_date(user_id=user_id)

    # list of portfolio dates and daily returns
    holding_percentage_rates = await get_portfolio_holding_percentage_rates(
        market_values=market_values, cash_transactions_by_date=cash_transactions_by_date
    )

    # Portfolio Return History Finished
    rate = Decimal(1)
    return_history_with_dates = []
    return_history_twrs = []
    for hpr in holding_percentage_rates:
        rate = rate * (hpr.hp + Decimal(1))
        return_history_with_dates.append(
            HistoricalReturn(
                date=hpr.date,
                daily_return=rate - 1,
            )
        )
        return_history_twrs.append(rate - Decimal(1))

    # Benchmark Return History
    # TODO ... change this out to an actual id
    benchmark_return_history = await compute_benchmark(benchmark_id=9876)

    rate = Decimal(1)
    benchmark_twrs_with_dates = []
    benchmark_twrs = []
    for brh in benchmark_return_history:
        rate = rate * (brh.hp + Decimal(1))
        benchmark_twrs_with_dates.append(HistoricalReturn(date=brh.date, daily_return=rate - 1))
        benchmark_twrs.append(rate - Decimal(1))

    # Time Weighted Return Finished
    time_weighted_return = return_history_with_dates[len(return_history_with_dates) - 1].daily_return

    # TODO:
    #   portfolio_allocation
    #   beta
    #   sharpe_ratio
    #   percentage_long
    #   percentage_short
    #   percentage_gross
    #   percentage_net
    return PortfolioResponse(
        user_id=user_id,
        return_history=return_history_with_dates,
        benchmark_return_history=benchmark_twrs_with_dates,
        total_return=time_weighted_return,
        beta=Decimal(0),
        sharpe_ratio=Decimal(0),
        percentage_long=Decimal(0),
        percentage_short=Decimal(0),
        percentage_gross=Decimal(0),
        percentage_net=Decimal(0),
        portfolio_type=PortfolioType.Creator if is_creator else PortfolioType.User,
    )


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
    market_value_by_day_response = await session.execute(
        select(
            FinancialAccountHoldingsHistory.holding_date,
            label(
                "market_value",
                func.sum(FinancialAccountHoldingsHistory.price * FinancialAccountHoldingsHistory.quantity),
            ),
        )
        .where(FinancialAccountHoldingsHistory.account_id == account_id)
        .group_by(FinancialAccountHoldingsHistory.holding_date)
        .order_by(FinancialAccountHoldingsHistory.holding_date.asc())
    )
    results = market_value_by_day_response.all()
    market_values = [MarketValue.parse_obj(res._asdict()) for res in results]
    return market_values


@Session
async def get_market_values(session: AsyncSession, user_id: int) -> list[MarketValue]:
    market_value_by_day_response = await session.execute(
        select(
            FinancialAccountHoldingsHistory.holding_date.label("date"),
            label(
                "value",
                func.sum(FinancialAccountHoldingsHistory.price * FinancialAccountHoldingsHistory.quantity),
            ),
        )
        .join(FinancialAccounts)
        .where(FinancialAccounts.user_id == user_id)
        .group_by(FinancialAccountHoldingsHistory.holding_date)
        .order_by(FinancialAccountHoldingsHistory.holding_date.asc())
    )

    results = market_value_by_day_response.all()
    market_values = [MarketValue.parse_obj(res._asdict()) for res in results]
    return market_values


async def get_portfolio_holding_percentage_rates(
    market_values: list[MarketValue], cash_transactions_by_date: dict[date, list[FinancialAccountTransactions]]
) -> list[HistoricalPeriod]:
    hpr_history = [
        HistoricalPeriod(
            date=market_values[0].date,
            mv=market_values[0].value,
            hp=0,
        )
    ]

    for index, _ in enumerate(market_values[1:]):
        mv_today = market_values[index].value
        mv_today_date = market_values[index].date
        mv_yesterday = hpr_history[len(hpr_history) - 1].mv

        # Two if statements factor subtract deposits / add back withdraws
        # dividends / interest fees / etc, are already added in via holdings history
        if mv_today_date in cash_transactions_by_date:
            mv_today = modify_market_value_by_cash_flow(
                market_value=mv_today, transactions=cash_transactions_by_date[mv_today_date]
            )

        hpr_history.append(
            HistoricalPeriod(
                date=mv_today_date,
                mv=mv_today,
                hp=(mv_today - mv_yesterday) / mv_yesterday,
            )
        )

    return hpr_history


def modify_market_value_by_cash_flow(
    market_value: Decimal, transactions: list[FinancialAccountTransactions]
) -> Decimal:
    for tx in transactions:
        if tx.type != "cash" or tx.type != "buy":
            continue
        if tx.subtype == "contribution":
            market_value = market_value - tx.value_amount
        if tx.subtype == "deposit":
            market_value = market_value - tx.value_amount
        if tx.subtype == "withdraw":
            market_value = market_value + tx.value_amount
    return market_value


@Session
async def compute_benchmark(session: AsyncSession, benchmark_id: int) -> list[HistoricalPeriod]:
    response = await session.execute(
        select(SecurityPrices)
        .where(SecurityPrices.security_id == benchmark_id)
        .order_by(SecurityPrices.price_time.asc())
    )

    all = response.scalars().all()

    hpr_history = [
        HistoricalPeriod(
            date=all[0].price_time,
            mv=all[0].price,
            hp=0,
        )
    ]

    for r in all[1:]:
        yesterday = hpr_history[len(hpr_history) - 1]
        hp = (r.price - yesterday.mv) / yesterday.mv
        hpr_history.append(
            HistoricalPeriod(
                date=r.price_time,
                mv=r.price,
                hp=hp,
            )
        )
    return hpr_history


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
async def get_user_baseline_holdings(session: AsyncSession, user_id: str) -> list:
    response = await session.execute(
        select(FinancialAccountHoldingsHistory, PlaidSecurities)
        .join(PlaidSecurities)
        .join(FinancialAccounts)
        .where(
            FinancialAccounts.user_id == user_id,
            FinancialAccountHoldingsHistory.holding_date
            == select(func.min(FinancialAccountHoldingsHistory.holding_date)),
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
