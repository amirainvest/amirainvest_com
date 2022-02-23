import datetime
from datetime import date
from decimal import Decimal
from typing import Optional

import numpy as np
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func, label

from backend_amirainvest_com.api.backend.portfolio.model import (
    HistoricalReturn,
    HistoricalTrade,
    Holding,
    HoldingPeriod,
    HoldingsResponse,
    MarketValue,
    PortfolioResponse,
    PortfolioType,
    PortfolioValue,
    SectionAllocation,
    TradingHistoryResponse,
)
from common_amirainvest_com.schemas.schema import (
    FinancialAccountHoldingsHistory,
    FinancialAccounts,
    FinancialAccountTransactions,
    PlaidSecurities,
    Securities,
    SecurityPrices,
    Users,
    UserSubscriptions,
)
from common_amirainvest_com.utils.decorators import Session


async def get_portfolio_trades(user_id: str, creator_id: str) -> TradingHistoryResponse:
    creator, is_creator = await get_user_and_if_creator(user_id=user_id, creator_id=creator_id)
    trading_history = await get_trading_history(user_id=creator.id)
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
                percentage_change_in_position=None,
            )
        )
    return TradingHistoryResponse(
        portfolio_type=PortfolioType.Creator if is_creator else PortfolioType.User, trades=response
    )


async def get_portfolio_holdings(user_id: str, creator_id: str) -> HoldingsResponse:
    creator, is_creator = await get_user_and_if_creator(user_id=user_id, creator_id=creator_id)
    holdings = await get_user_holdings_with_securities_data(user_id=creator.id)
    portfolio = get_portfolio_value(holdings=holdings, user_id=creator.id)

    response: list[Holding] = []
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

    return HoldingsResponse(
        portfolio_type=PortfolioType.Creator if is_creator else PortfolioType.User, holdings=response
    )


async def get_portfolio_summary(user_id: str, creator_id: str, start_date: date, end_date: date) -> PortfolioResponse:
    creator, is_creator = await get_user_and_if_creator(user_id=user_id, creator_id=creator_id)
    plaid_cash_security = await get_cash_security_plaid()
    market_values = await get_market_values(user_id=creator.id, start_date=start_date, end_date=end_date)
    cash_transactions = await get_cash_transactions_by_date(
        user_id=creator.id, start_date=start_date, end_date=end_date
    )

    # Portfolio Historical Holding Period Rates
    portfolio_holding_periods = await get_portfolio_holding_percentage_rates(
        market_values=market_values, cash_transactions=cash_transactions
    )

    # Portfolio Time Weighted Return History
    twr_rate = Decimal(1)
    portfolio_historical_time_weighted_returns = []
    for php in portfolio_holding_periods:
        twr_rate = twr_rate * (php.rate + Decimal(1))
        portfolio_historical_time_weighted_returns.append(
            HistoricalReturn(
                date=php.date,
                daily_return=twr_rate - 1,
            )
        )

    # Benchmark Historical Holding Period Rates
    benchmark_holding_periods = await compute_benchmark(
        benchmark_id=creator.benchmark, dates=(d.date for d in portfolio_holding_periods)
    )

    # Benchmark Time Weighted Return History
    benchmark_twr_rate = Decimal(1)
    benchmark_historical_time_weighted_returns = []
    for b_hp in benchmark_holding_periods:
        benchmark_twr_rate = benchmark_twr_rate * (b_hp.rate + Decimal(1))
        benchmark_historical_time_weighted_returns.append(
            HistoricalReturn(date=b_hp.date, daily_return=benchmark_twr_rate - 1)
        )

    # Time Weighted Return Finished
    portfolio_holding_period_rates = [float(php.rate) for php in portfolio_holding_periods]
    benchmark_holding_period_rates = [float(bhp.rate) for bhp in benchmark_holding_periods]
    covariance = np.cov(portfolio_holding_period_rates, benchmark_holding_period_rates)[0][1]
    variance = np.var(benchmark_holding_period_rates, ddof=1)
    beta = covariance / variance

    current_holdings = await get_current_holdings_from_history(user_id=creator.id)
    sharpe_ratio = await compute_sharpe_ratio(portfolio_returns=portfolio_holding_periods)

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

    portfolio_allocation = await get_portfolio_allocation(user_id=creator.id)
    return PortfolioResponse(
        user_id=creator.id,
        portfolio_allocation=portfolio_allocation,
        return_history=portfolio_historical_time_weighted_returns,
        benchmark_return_history=benchmark_historical_time_weighted_returns,
        total_return=portfolio_historical_time_weighted_returns[
            len(portfolio_historical_time_weighted_returns) - 1
        ].daily_return,
        beta=beta,
        sharpe_ratio=sharpe_ratio,
        percentage_long=long,
        percentage_short=short,
        percentage_gross=gross,
        percentage_net=net,
        portfolio_type=PortfolioType.Creator if is_creator else PortfolioType.User,
    )


async def compute_sharpe_ratio(portfolio_returns: list[HoldingPeriod]) -> Decimal:
    portfolio_returns.sort(key=lambda x: x.date)
    vals = []
    for pr in portfolio_returns:
        vals.append(float(pr.rate))
    mean = np.mean(vals, dtype=np.float64)
    std_dev = np.std(vals, ddof=1, dtype=np.float64)
    return Decimal(mean / std_dev)


def get_portfolio_value(holdings: list, user_id: str) -> PortfolioValue:
    portfolio_value = PortfolioValue(user_id=user_id, value=0)
    for holding in holdings:
        fa = holding.FinancialAccountCurrentHoldings
        value = portfolio_value.value + Decimal(fa.quantity * fa.latest_price)
        portfolio_value.value = value

    return portfolio_value


@Session
async def get_user_and_if_creator(session: AsyncSession, user_id: str, creator_id: str) -> tuple[Users, bool]:
    if user_id == creator_id:
        response = (await session.execute(select(Users).where(Users.id == creator_id))).scalar_one()
        return response, False

    response = await session.execute(
        select(Users)
        .join(UserSubscriptions, UserSubscriptions.subscriber_id == Users.id)
        .where(UserSubscriptions.subscriber_id == user_id, UserSubscriptions.creator_id == creator_id)
    )

    user = response.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user is not a subscriber of the creator")
    return user, True


@Session
async def get_user(session: AsyncSession, user_id: str) -> Users:
    response = await session.execute(select(Users).where(Users.id == user_id))
    return response.scalar_one()


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
        if sector is None:
            continue
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
) -> list[HoldingPeriod]:
    yesterday = HoldingPeriod(
        date=market_values[0].date,
        market_value=market_values[0].value,
        rate=0,
    )
    hpr_history = [yesterday]
    for mv in market_values[1:]:
        if mv.date in cash_transactions:
            mv.value = mv.value + cash_transactions[mv.date]
        hpr_today = HoldingPeriod(
            date=mv.date,
            market_value=mv.value,
            rate=(mv.value - yesterday.market_value) / yesterday.market_value,
        )
        hpr_history.append(hpr_today)
        yesterday = hpr_today
    return hpr_history


@Session
async def compute_benchmark(
    session: AsyncSession, benchmark_id: Optional[int], dates: set[date]
) -> list[HoldingPeriod]:
    if benchmark_id is None:
        benchmark_id = (
            (await session.execute(select(Securities).where(Securities.ticker_symbol == "SPY"))).scalar_one()
        ).id

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
        HoldingPeriod(
            date=all[0].price_time,
            market_value=all[0].price,
            rate=0,
        )
    ]

    for r in all[1:]:
        yesterday = hpr_history[len(hpr_history) - 1]
        hp = (r.price - yesterday.market_value) / yesterday.market_value
        hpr_history.append(
            HoldingPeriod(
                date=r.price_time,
                market_value=r.price,
                rate=hp,
            )
        )
    hpr_history.sort(key=lambda x: x.date)
    return hpr_history


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
async def get_trading_history(session: AsyncSession, user_id: str) -> list:
    response = await session.execute(
        select(FinancialAccountTransactions, PlaidSecurities)
        .join(FinancialAccounts)
        .join(PlaidSecurities)
        .where(FinancialAccounts.user_id == user_id)
        .order_by(FinancialAccountTransactions.posting_date.desc())
    )
    return response.all()
