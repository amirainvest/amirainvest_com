import uuid

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.schemas.schema import (
    FinancialAccountCurrentHoldings, Securities, SecurityPrices,
    PlaidSecurities,
)
from typing import Optional


@Session
async def get_holdings(session: AsyncSession, user_id: uuid.UUID) -> [FinancialAccountCurrentHoldings]:
    return (await session.execute(
        select(FinancialAccountCurrentHoldings).where(FinancialAccountCurrentHoldings.user_id == user_id)
    )).scalars().all()


@Session
async def get_recent_stock_price(session: AsyncSession, ticker_symbol: str) -> Optional[SecurityPrices]:
    # We want to do a join and get the price of a security by symbol most recent time
    return (await session.execute(
        select(SecurityPrices)
            .join(Securities.id)
            .where(Securities.ticker_symbol == ticker_symbol)
            .order(desc(SecurityPrices.price_time))
            .limit(1)
    )).one_or_none()


@Session
async def get_ticker_symbol_by_plaid_id(session: AsyncSession, plaid_id: int) -> Optional[PlaidSecurities]:
    return (await session.execute(
        select(PlaidSecurities).where(PlaidSecurities.id == plaid_id)
    )).one_or_none()


@Session
async def get_portfolio_value(session: AsyncSession, user_id: uuid.UUID):
    pass


@Session
async def get_buy_date(session: AsyncSession, user_id: uuid.UUID, security_id: int):
    pass
