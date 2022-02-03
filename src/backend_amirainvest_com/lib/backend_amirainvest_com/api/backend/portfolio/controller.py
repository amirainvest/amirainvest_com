import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.backend.portfolio.model import PortfolioValue
from common_amirainvest_com.schemas.schema import (
    FinancialAccountCurrentHoldings,
    FinancialAccounts,
    FinancialAccountTransactions,
    PlaidSecurities,
    Securities,
    SecurityPrices,
)
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_holdings(session: AsyncSession, user_id: uuid.UUID) -> list[FinancialAccountCurrentHoldings]:
    return (
        (
            await session.execute(
                select(FinancialAccountCurrentHoldings).where(FinancialAccountCurrentHoldings.user_id == user_id)
            )
        )
        .scalars()
        .all()
    )


@Session
async def get_recent_stock_price(session: AsyncSession, ticker_symbol: str) -> Optional[SecurityPrices]:
    # We want to do a join and get the price of a security by symbol most recent time
    return (
        await session.execute(
            select(SecurityPrices)
            .join(Securities.id)
            .where(Securities.ticker_symbol == ticker_symbol)
            .order_by(desc(SecurityPrices.price_time))
            .limit(1)
        )
    ).scalar()


@Session
async def get_buy_date(
    session: AsyncSession, user_id: uuid.UUID, security_id: int, position_quantity: int
) -> Optional[datetime]:
    transactions_response = await session.execute(
        select(FinancialAccountTransactions)
        .join(FinancialAccounts.id)
        .where(FinancialAccounts.user_id == user_id, FinancialAccountTransactions.security_id == security_id)
        .order_by(asc(FinancialAccountTransactions.posting_date))
    )
    transactions = transactions_response.scalars().all()

    buy_date, qty = compute_buy_date(Decimal(0), transactions)
    if qty == position_quantity:
        return buy_date
    return compute_buy_date(Decimal(abs(position_quantity - qty)), transactions)[0]


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
async def get_portfolio_value(session: AsyncSession, user_id: uuid.UUID) -> PortfolioValue:
    holdings_response = await session.execute(
        select(FinancialAccountCurrentHoldings).where(FinancialAccountCurrentHoldings.user_id == user_id)
    )

    holdings = holdings_response.scalars().all()
    portfolio_value = PortfolioValue(user_id=user_id, value=0)
    for holding in holdings:
        value = portfolio_value.value + Decimal(holding.quantity * holding.latest_price)
        portfolio_value.value = value

    return portfolio_value
