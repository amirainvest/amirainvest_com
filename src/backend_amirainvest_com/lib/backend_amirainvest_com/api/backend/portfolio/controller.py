from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import (
    FinancialAccountCurrentHoldings,
    FinancialAccounts,
    FinancialAccountTransactions,
    PlaidSecurities,
    Securities,
    SecurityPrices,
    UserSubscriptions,
)
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_user_subscription(session: AsyncSession, user_id: str, creator_id: str) -> Optional[UserSubscriptions]:
    response = await session.execute(
        select(UserSubscriptions)
        .where(UserSubscriptions.subscriber_id == user_id)
        .where(UserSubscriptions.creator_id == creator_id)
    )
    return response.scalar()


@Session
async def get_holdings(session: AsyncSession, user_id: str) -> list:
    response = await session.execute(
        select(FinancialAccountCurrentHoldings, PlaidSecurities)
        .join(PlaidSecurities)
        .where(
            FinancialAccountCurrentHoldings.user_id == user_id,
            PlaidSecurities.id == FinancialAccountCurrentHoldings.plaid_security_id,
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
async def get_buy_date(
    session: AsyncSession, user_id: str, security_id: int, position_quantity: int
) -> Optional[datetime]:
    transactions_response = await session.execute(
        select(FinancialAccountTransactions)
        .join(FinancialAccounts)
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
async def get_trading_history(session: AsyncSession, user_id: str) -> list:
    response = await session.execute(
        select(FinancialAccountTransactions, PlaidSecurities)
        .join(FinancialAccounts)
        .join(PlaidSecurities)
        .where(FinancialAccounts.user_id == user_id)
        .order_by(FinancialAccountTransactions.posting_date.desc())
    )
    return response.all()
