from datetime import datetime
from typing import Optional

from dateutil import relativedelta
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.functions import max
from sqlalchemy.types import Date, Time

from backend_amirainvest_com.api.backend.company_route.model import CompanyResponse
from common_amirainvest_com.schemas.schema import Securities, SecurityInformation, SecurityPrices
from common_amirainvest_com.utils.decorators import Session


async def get_company_breakdown(ticker_symbol: str) -> CompanyResponse:
    security_meta = await get_security_info(ticker_symbol)
    security_information = security_meta.SecurityInformation
    security = security_meta.Securities

    if not security.collect:
        # TODO intraday & five-day will not be available and we should make a call to IEX
        await toggle_company_on(security.id)

    max_eod_pricing = await get_eod_pricing(security_id=security.id)
    intraday_pricing = await get_minute_pricing(security_id=security.id)
    five_day_pricing = await get_hour_pricing(security_id=security.id)

    return CompanyResponse(
        name=security.humand_readable_name,
        ticker=security.ticker_symbol,
        industry=security.industry,
        ceo=security.ceo,
        asset_type=security.asset_type,
        founding_date=security.founding_date,
        description=security.description,
        week_high_52=security_information.week_high_52,
        week_low_52=security_information.week_low_52,
        open=security_information.open,
        close=security_information.close,
        market_cap=security_information.market_cap,
        average_volume=security_information.average_total_volume,
        intraday_pricing=intraday_pricing,
        max_eod_pricing=max_eod_pricing,
        five_day_pricing=five_day_pricing,
    )


@Session
async def get_security_info(session: AsyncSession, ticker_symbol: str) -> Optional[Securities]:
    response = await session.execute(
        select(Securities, SecurityInformation)
        .join(SecurityInformation)
        .where(Securities.ticker_symbol == ticker_symbol)
    )
    return response.scalar()


@Session
async def toggle_company_on(session: AsyncSession, security_id: int):
    await session.execute(update(Securities).where(Securities.id == security_id).values({"collect": True}))


hrs = ["10:00:00", "11:00:00", "12:00:00", "13:00:00", "14:00:00", "15:00:00", "16:00:00"]


@Session
async def get_hour_pricing(session: AsyncSession, security_id: int) -> list[SecurityPrices]:
    today = datetime.utcnow()
    seven_days = today - relativedelta.relativedelta(days=7)
    response = await session.execute(
        select(SecurityPrices).where(
            SecurityPrices.security_id == security_id,
            SecurityPrices.price_time.between(today, seven_days),
            cast(SecurityPrices.price_time.in_(hrs), Time),
        )
    )
    return response.scalars().all()


@Session
async def get_minute_pricing(session: AsyncSession, security_id: int) -> list[SecurityPrices]:
    response = await session.execute(
        select(SecurityPrices).where(
            SecurityPrices.security_id == security_id,
            cast(SecurityPrices.price_time, Date)
            == cast(select(max(SecurityPrices.price_time)).where(SecurityPrices.security_id == security_id), Date),
        )
    )
    return response.scalars().all()


@Session
async def get_eod_pricing(session: AsyncSession, security_id: int) -> list[SecurityPrices]:
    response = await session.execute(
        select(SecurityPrices.price, SecurityPrices.price_time)
        .distinct(cast(SecurityPrices.price_time, Date))
        .where(SecurityPrices.security_id == security_id)
        .order_by(SecurityPrices.price_time.desc())
    )

    return response.scalars().all()
