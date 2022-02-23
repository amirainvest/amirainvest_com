import datetime
from datetime import date
from decimal import Decimal
from typing import Optional

import numpy as np
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
    SectionAllocation,
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
                percentage_change_in_position=None,  # TODO ...
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


async def get_portfolio_summary(user_id: str, is_creator: bool, start_date: date, end_date: date) -> PortfolioResponse:
    plaid_cash_security = await get_cash_security_plaid()
    market_values = await get_market_values(user_id=user_id, start_date=start_date, end_date=end_date)
    cash_transactions = await get_cash_transactions_by_date(user_id=user_id, start_date=start_date, end_date=end_date)

    # list of portfolio dates and daily returns
    portfolio_hprs = await get_portfolio_holding_percentage_rates(
        market_values=market_values, cash_transactions=cash_transactions
    )

    # Portfolio Return History Finished
    rate = Decimal(1)
    return_history_with_dates = []
    return_history_twrs: list[float] = []
    return_history_dates: set[date] = set()
    for hpr in portfolio_hprs:
        rate = rate * (hpr.hp + Decimal(1))
        return_history_dates.add(hpr.date)
        return_history_with_dates.append(
            HistoricalReturn(
                date=hpr.date,
                daily_return=rate - 1,
            )
        )
        return_history_twrs.append(float(hpr.hp))

    # Benchmark Return History
    # TODO ....
    benchmark_return_history = await compute_benchmark(benchmark_id=9876, dates=return_history_dates)

    rate = Decimal(1)
    benchmark_twrs_with_dates = []
    benchmark_twrs: list[float] = []
    for brh in benchmark_return_history:
        rate = rate * (brh.hp + Decimal(1))
        benchmark_twrs_with_dates.append(HistoricalReturn(date=brh.date, daily_return=rate - 1))
        benchmark_twrs.append(float(brh.hp))

    # Time Weighted Return Finished
    time_weighted_return = return_history_with_dates[len(return_history_with_dates) - 1].daily_return
    covariance = np.cov(return_history_twrs, benchmark_twrs)[0][1]
    variance = np.var(benchmark_twrs, ddof=1)
    beta = covariance / variance

    current_holdings = await get_current_holdings_from_history(user_id=user_id)
    sharpe_ratio = await compute_sharpe_ratio(portfolio_returns=return_history_with_dates)

    cash = Decimal(0)
    mv = Decimal(0)
    long_pos = Decimal(0)
    short_pos = Decimal(0)
    for ch in current_holdings:
        mv = mv + (ch.quantity * ch.price)
        if ch.plaid_security_id == plaid_cash_security.id:
            cash = cash + ch.quantity
        if ch.quantity > 0:
            long_pos = long_pos + (ch.quantity * ch.price)
        if ch.quantity < 0:
            short_pos = short_pos + (ch.quantity * ch.price)

    long = (long_pos - cash) / mv
    short = abs(short_pos) / mv
    gross = (long_pos + abs(short_pos) - cash) / mv
    net = ((long_pos + short_pos) - cash) / mv

    portfolio_allocation = await get_portfolio_allocation(user_id=user_id)
    return PortfolioResponse(
        user_id=user_id,
        portfolio_allocation=portfolio_allocation,
        return_history=return_history_with_dates,
        benchmark_return_history=benchmark_twrs_with_dates,
        total_return=time_weighted_return,
        beta=beta,
        sharpe_ratio=sharpe_ratio,
        percentage_long=long,
        percentage_short=short,
        percentage_gross=gross,
        percentage_net=net,
        portfolio_type=PortfolioType.Creator if is_creator else PortfolioType.User,
    )


@Session
async def compute_sharpe_ratio(session: AsyncSession, portfolio_returns: list[HistoricalReturn]) -> Decimal:
    portfolio_returns.sort(key=lambda x: x.date)
    dates = []
    for pr in portfolio_returns:
        dt = datetime.datetime.combine(pr.date, datetime.datetime.min.time())
        dt = dt.replace(hour=21)
        dates.append(dt)

    response = await session.execute(
        select(SecurityPrices)
        .join(Securities)
        .where(Securities.ticker_symbol == "US02Y", SecurityPrices.price_time.in_(dates))
        .order_by(SecurityPrices.price_time.desc())
    )
    excess_return = []
    benchmark_prices = response.scalars().all()

    idx = 0
    while idx < len(portfolio_returns):
        daily_return = portfolio_returns[idx].daily_return
        benchmark_price = benchmark_prices[idx].price
        excess_return.append(float(daily_return) - float(benchmark_price))
        idx = idx + 1

    std_dev = float(np.std(excess_return, ddof=1, dtype=np.float64))
    return Decimal(std_dev)


@Session
async def get_cash_security_plaid(session: AsyncSession) -> Optional[PlaidSecurities]:
    response = await session.execute(select(PlaidSecurities).where(PlaidSecurities.ticker_symbol == "CUR:USD"))
    return response.scalar()


@Session
async def get_cash_transactions_by_date(
    session: AsyncSession, user_id: int, start_date: date, end_date: date
) -> dict[date, Decimal]:
    transactions_response = await session.execute(
        select(FinancialAccountTransactions)
        .join(FinancialAccounts)
        .where(
            FinancialAccounts.user_id == user_id,
            FinancialAccountTransactions.posting_date >= start_date,
            FinancialAccountTransactions.posting_date <= end_date,
        )
    )
    transactions = transactions_response.scalars().all()

    d: dict[date, Decimal] = {}
    for tx in transactions:
        if tx.type != "cash" or tx.type != "buy":
            continue
        """
            Contribution +
            Deposit +
            Withdraw -
        """
        value = Decimal(tx.value_amount * -1)
        try:
            d[tx.posting_date.date()] = d[tx.posting_date.date()] + value
        except KeyError:
            d[tx.posting_date.date()] = value
    return d


@Session
async def get_portfolio_allocation(session: AsyncSession, user_id: int) -> list[SectionAllocation]:
    response = await session.execute(
        select(FinancialAccountHoldingsHistory, Securities)
        .join(FinancialAccounts)
        .join(Securities)
        .where(
            FinancialAccounts.user_id == user_id,
            FinancialAccountHoldingsHistory.holding_date
            == select(func.min(FinancialAccountHoldingsHistory.holding_date)),
        )
    )

    sector_allocation: dict[str, Decimal] = {}

    total_allocation = Decimal(0)
    for res in response.all():
        allocation = abs((res.FinancialAccountHoldingsHistory.quantity * res.FinancialAccountHoldingsHistory.price))
        total_allocation = total_allocation + allocation
        try:
            sector_allocation[res.Securities.industry] = sector_allocation[res.Securities.industry] + allocation
        except KeyError:
            sector_allocation[res.Securities.industry] = allocation

    allocations: list[SectionAllocation] = []
    for sector in sector_allocation:
        allocation = sector_allocation[sector]
        allocations.append(SectionAllocation(name=sector, percentage=allocation / total_allocation))
    return allocations


@Session
async def get_market_values(session: AsyncSession, user_id: int, start_date: date, end_date: date) -> list[MarketValue]:
    market_value_by_day_response = await session.execute(
        select(
            FinancialAccountHoldingsHistory.holding_date.label("date"),
            label(
                "value",
                func.sum(FinancialAccountHoldingsHistory.price * FinancialAccountHoldingsHistory.quantity),
            ),
        )
        .join(FinancialAccounts)
        .where(
            FinancialAccounts.user_id == user_id,
            FinancialAccountHoldingsHistory.holding_date >= start_date,
            FinancialAccountHoldingsHistory.holding_date <= end_date,
        )
        .group_by(FinancialAccountHoldingsHistory.holding_date)
        .order_by(FinancialAccountHoldingsHistory.holding_date.asc())
    )

    results = market_value_by_day_response.all()
    market_values = [MarketValue.parse_obj(res._asdict()) for res in results]
    return market_values


async def get_portfolio_holding_percentage_rates(
    market_values: list[MarketValue], cash_transactions: dict[date, Decimal]
) -> list[HistoricalPeriod]:
    yesterday = HistoricalPeriod(
        date=market_values[0].date,
        mv=market_values[0].value,
        hp=0,
    )
    hpr_history = [yesterday]
    for mv in market_values[1:]:
        if mv.date in cash_transactions:
            mv.value = mv.value + cash_transactions[mv.date]
        hpr_today = HistoricalPeriod(
            date=mv.date,
            mv=mv.value,
            hp=(mv.value - yesterday.mv) / yesterday.mv,
        )
        hpr_history.append(hpr_today)
        yesterday = hpr_today
    return hpr_history


@Session
async def compute_benchmark(session: AsyncSession, benchmark_id: int, dates: set[date]) -> list[HistoricalPeriod]:
    date_times = []
    for d in dates:
        dt = datetime.datetime.combine(d, datetime.datetime.min.time())
        dt = dt.replace(hour=21)
        date_times.append(dt)

    response = await session.execute(
        select(SecurityPrices)
        .where(SecurityPrices.security_id == benchmark_id, SecurityPrices.price_time.in_(date_times))
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

    hpr_history.sort(key=lambda x: x.date)
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
async def get_current_holdings_from_history(
    session: AsyncSession, user_id: str
) -> list[FinancialAccountHoldingsHistory]:
    response = await session.execute(
        select(FinancialAccountHoldingsHistory)
        .join(FinancialAccounts)
        .where(
            FinancialAccounts.user_id == user_id,
            FinancialAccountHoldingsHistory.holding_date
            == select(func.max(FinancialAccountHoldingsHistory.holding_date)),
        )
    )
    return response.scalars().all()


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
