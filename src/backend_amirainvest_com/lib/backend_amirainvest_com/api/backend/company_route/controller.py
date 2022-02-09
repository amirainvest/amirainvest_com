from datetime import datetime
from common_amirainvest_com.schemas.schema import Securities, SecurityPrices
from common_amirainvest_com.utils.decorators import Session
from sqlalchemy import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.functions import max
from sqlalchemy import update, cast, Date
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously


@Session
async def get_security_info(session: AsyncSession, ticker_symbol: str) -> Securities:
    response = await session.execute(select(Securities).where(Securities.ticker_symbol == ticker_symbol))
    return response.scalar()


@Session
async def toggle_company_on(session: AsyncSession, security_id: int):
    await session.execute(
        update(Securities).where(Securities.id == security_id).values({'collect': True})
    )


@Session
async def get_minute_pricing(session: AsyncSession, security_id: int) -> list[SecurityPrices]:
    response = await session.execute(
        select(SecurityPrices)
            .where(
            SecurityPrices.security_id == security_id,
            cast(SecurityPrices.price_time, Date) == cast(
                select(max(SecurityPrices.price_time)).where(
                    SecurityPrices.security_id == security_id
                ), Date
            )
        )
    )
    return response.scalars().all()


""""
A couple ways we could fetch all pricing
1. Build a query and do a CTE and get all max records closest to x minute
2. When we are fetching real-time pricing if price is on the hour / minute
    -- add to db array(or chuck into another process that will ingest it)
3.
"""


@Session
async def get_hourly_pricing(session: AsyncSession, security_id: int):
    response = await session.execute(

    )


async def r():
    res = await get_minute_pricing(24)
    for r in res:
        print(vars(r))


if __name__ == '__main__':
    run_async_function_synchronously(r)
