from datetime import datetime, time

import pytz
from dateutil import relativedelta
from pytz import timezone
from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import cast
from sqlalchemy.sql.functions import max
from sqlalchemy.types import Date, Time

from backend_amirainvest_com.api.backend.company_route.model import CompanyResponse, ListedCompany, SecurityPrice
from common_amirainvest_com.iex.client import get_historical_five_day_pricing, get_intraday_prices
from common_amirainvest_com.schemas.schema import Securities, SecurityInformation, SecurityPrices
from common_amirainvest_com.utils.decorators import Session


async def get_company_breakdown(ticker_symbol: str) -> CompanyResponse:
    security_meta = await get_security_info(ticker_symbol=ticker_symbol)
    security_information = security_meta.SecurityInformation
    security = security_meta.Securities

    if security_information is None:
        security_information = SecurityInformation()

    max_eod_pricing = await get_eod_pricing(security_id=security.id)
    prices: list[SecurityPrice] = []
    for mp in max_eod_pricing:
        prices.append(SecurityPrice(price_time=mp[1], price=mp[0]))

    return CompanyResponse(
        name=security.name,
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
        max_eod_pricing=prices,
    )


async def get_five_day_pricing(ticker_symbol: str) -> list[SecurityPrice]:
    security_meta = await get_security_info(ticker_symbol=ticker_symbol)
    security = security_meta.Securities
    five_day_pricing = await get_hour_pricing(security_id=security.id)
    response: list[SecurityPrice] = []

    if five_day_pricing is not None and len(five_day_pricing) > 5:
        for fdp in five_day_pricing:
            response.append(SecurityPrice(price_time=fdp.price_time, price=fdp.price))
        return response

    historical_prices = await get_historical_five_day_pricing(symbol=security.ticker_symbol)

    five_day_pricing = []
    et_tz = timezone("US/Eastern")
    for hp in historical_prices:
        if hp.marketOpen is None:
            continue
        if hp.label is None or hp.label == "":
            continue
        if hp.date is None or hp.date == "":
            continue
        price_time_str = f"{hp.date} {hp.label}"
        price_time = et_tz.localize(datetime.strptime(price_time_str, "%Y-%m-%d %H:%M"))
        price_time = price_time.astimezone(pytz.utc).replace(tzinfo=None)
        p = SecurityPrices(security_id=security.id, price=hp.marketOpen, price_time=price_time)
        response.append(SecurityPrice(price_time=price_time, price=hp.marketOpen))
        five_day_pricing.append(p.dict())
    await bulk_add_pricing(five_day_pricing)
    return response


async def get_intraday_pricing(ticker_symbol: str) -> list[SecurityPrice]:
    security_meta = await get_security_info(ticker_symbol=ticker_symbol)
    security = security_meta.Securities

    collecting_pricing = security.collect
    if not collecting_pricing:
        await toggle_company_on(security.id)
    intraday_pricing = await get_minute_pricing(security_id=security.id)

    response: list[SecurityPrice] = []
    if not collecting_pricing or (len(intraday_pricing) <= 1 and datetime.utcnow().time() > time(14, 35)):
        return await fetch_and_add_pricing(security)

    for ip in intraday_pricing:
        response.append(SecurityPrice(price_time=ip.price_time, price=ip.price))
    return response


async def fetch_and_add_pricing(security: Securities) -> list[SecurityPrice]:
    intraday_prices = await get_intraday_prices(symbol=security.ticker_symbol)
    intraday_pricing = []
    response: list[SecurityPrice] = []
    et_tz = timezone("US/Eastern")
    for ip in intraday_prices:
        if ip.open is None:
            continue
        if ip.label is None or ip.label == "":
            continue
        if ip.date is None or ip.date == "":
            continue

        price_time_str = f"{ip.date} {ip.label}"
        price_time = et_tz.localize(datetime.strptime(price_time_str, "%Y-%m-%d %I:%M %p"))
        price_time = price_time.astimezone(pytz.utc).replace(tzinfo=None)
        p = SecurityPrices(security_id=security.id, price=ip.open, price_time=price_time)
        response.append(SecurityPrice(price_time=price_time, price=ip.open))
        intraday_pricing.append(p.dict())
    await bulk_add_pricing(intraday_pricing)
    return response


@Session
async def bulk_add_pricing(session: AsyncSession, security_prices: list[SecurityPrices]):
    if len(security_prices) <= 0:
        return
    await session.execute(insert(SecurityPrices).values(security_prices).on_conflict_do_nothing())


@Session
async def get_listed_companies(session: AsyncSession) -> list[ListedCompany]:
    response = await session.execute(select(Securities).where(Securities.issue_type.in_("cs", "ad", "et")))

    lcs: list[ListedCompany] = []
    for lc in response.scalars().all():
        lcs.append(ListedCompany(name=lc.name, ticker_symbol=lc.ticker_symbol))
    return lcs


@Session
async def get_security_info(session: AsyncSession, ticker_symbol: str) -> Row:
    response = await session.execute(
        select(Securities, SecurityInformation)
        .join(SecurityInformation, isouter=True)
        .where(Securities.ticker_symbol == ticker_symbol)
    )
    return response.one()


@Session
async def toggle_company_on(session: AsyncSession, security_id: int):
    await session.execute(update(Securities).where(Securities.id == security_id).values({"collect": True}))


@Session
async def get_hour_pricing(session: AsyncSession, security_id: int) -> list[SecurityPrices]:
    # TODO wonder if this would be better if we slugged in ET time, set ET as TZ and converted to UTC

    ten = datetime.utcnow().time().replace(hour=15, minute=0, second=0, microsecond=0)
    hr = 15
    hrs = [ten.replace(hour=hr + i) for i in range(1, 8)]
    today = datetime.utcnow()
    seven_days_ago = today - relativedelta.relativedelta(days=8)
    response = await session.execute(
        select(SecurityPrices).where(
            SecurityPrices.security_id == security_id,
            SecurityPrices.price_time >= seven_days_ago,
            SecurityPrices.price_time < today,
            cast(SecurityPrices.price_time, Time).in_(hrs),
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
async def get_eod_pricing(session: AsyncSession, security_id: int) -> list[Row]:
    response = await session.execute(
        select(SecurityPrices.price, SecurityPrices.price_time)
        .distinct(cast(SecurityPrices.price_time, Date))
        .where(SecurityPrices.security_id == security_id)
    )

    return response.all()
