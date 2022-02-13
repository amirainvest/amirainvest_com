import csv
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.s3.client import S3
from common_amirainvest_com.s3.consts import AMIRA_SECURITIES_HISTORICAL_PRICES_BUCKET
from common_amirainvest_com.schemas.schema import Securities, SecurityPrices, MarketHolidays
from common_amirainvest_com.utils.decorators import Session
from market_data_amirainvest_com.iex import HistoricalPrice


async def add_to_s3(historical_prices: list[HistoricalPrice], symbol: str, year: int):
    headers = [
        "close",
        "high",
        "low",
        "open",
        "symbol",
        "volume",
        "id",
        "key",
        "date",
        "updated",
        "changeOverTime",
        "marketChangeOverTime",
        "uOpen",
        "uClose",
        "uHigh",
        "uLow",
        "uVolume",
        "fOpen",
        "fClose",
        "fHigh",
        "fLow",
        "fVolume",
        "label",
        "change",
        "changePercent",
    ]
    rows = []
    for p in historical_prices:
        rows.append(
            [
                p.close,
                p.high,
                p.low,
                p.open,
                p.symbol,
                p.volume,
                p.id,
                p.key,
                p.date,
                p.updated,
                p.changeOverTime,
                p.marketChangeOverTime,
                p.uOpen,
                p.uClose,
                p.uHigh,
                p.uLow,
                p.uVolume,
                p.fOpen,
                p.fClose,
                p.fHigh,
                p.fLow,
                p.fVolume,
                p.label,
                p.change,
                p.changePercent,
            ]
        )

    file_name = f"{symbol}-{year}.csv"
    with open(file_name, "w+", encoding="UTF-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    s3 = S3()
    await s3.upload_file(file_name, AMIRA_SECURITIES_HISTORICAL_PRICES_BUCKET, f"{symbol}/{file_name}")


@Session
async def get_security_by_ticker_symbol(session: AsyncSession, ticker: str) -> Optional[Securities]:
    response = await session.execute(select(Securities).where(Securities.ticker_symbol == ticker))
    return response.scalar()


@Session
async def _security_price_time_exists(session: AsyncSession, security_id: int, price_time: datetime) -> bool:
    response = await session.execute(
        select(SecurityPrices).where(SecurityPrices.security_id == security_id, SecurityPrices.price_time == price_time)
    )

    if len(response.scalars().all()) > 0:
        return True
    return False


@Session
async def _add_securities_prices(session: AsyncSession, securities_prices: list) -> None:
    session.add_all(securities_prices)


def group_securities(securities: list[Securities], num_group: int) -> list[list[Securities]]:
    group = []
    sub_group = []
    for sec in securities:
        if sec.ticker_symbol is None or sec.ticker_symbol == "":
            continue
        sub_group.append(sec)
        if len(sub_group) >= num_group:
            group.append(sub_group)
            sub_group = []
    if len(sub_group) > 0:
        group.append(sub_group)
    return group


@Session
async def add_to_db(session: AsyncSession, security_id: int, historical_prices: list[HistoricalPrice]):
    price_times = []
    for h in historical_prices:
        if h.date is None:
            continue
        date = datetime.strptime(h.date, "%Y-%m-%d")
        price_times.append(date)

    response = await session.execute(
        select(SecurityPrices).where(
            SecurityPrices.price_time.in_(price_times), SecurityPrices.security_id == security_id
        )
    )

    current_price_times = response.scalars().all()

    price_time_map: dict[datetime, None] = {}
    for cur in current_price_times:
        price_time_map[cur.price_time] = None

    security_prices = []
    for p in historical_prices:
        if p.date is None or p.date == "":
            continue
        date = datetime.strptime(p.date, "%Y-%m-%d")
        if date in price_time_map:
            continue

        security_prices.append(
            SecurityPrices(
                security_id=security_id,
                # fClose = Fully Adjusted Close, close is split adjusted and uClose is unadjusted close
                # we use close though as we default to everything being fully-adjusted
                price=p.close,
                price_time=date,
            )
        )
    session.add_all(security_prices)


@Session
async def get_securities(session: AsyncSession) -> list[Securities]:
    response = await session.execute(select(Securities).where(Securities.issue_type.in_(("cs", "ad", "et"))))
    return response.scalars().all()


@Session
async def get_securities_collect_true(session: AsyncSession) -> list[Securities]:
    response = await session.execute(select(Securities).where(Securities.collect == True))  # noqa: E712
    return response.scalars().all()


@Session
async def add_securities_prices(session: AsyncSession, security_prices: list[SecurityPrices]):
    session.add_all(security_prices)


@Session
async def bulk_upsert_security_prices(session: AsyncSession, security_prices: list[SecurityPrices]):
    price_time = security_prices[0].price_time
    security_ids = []
    dict_prices = {}
    for sp in security_prices:
        security_ids.append(sp.security_id)
        dict_prices[sp.security_id] = sp

    response = await session.execute(
        select(SecurityPrices).where(
            SecurityPrices.price_time == price_time, SecurityPrices.security_id.in_(security_ids)
        )
    )

    cur_security_prices = response.scalars().all()
    for cur_sec_price in cur_security_prices:
        sec = dict_prices[cur_sec_price.security_id]
        cur_sec_price.price = sec.price
        del dict_prices[cur_sec_price.security_id]
    await session.commit()

    inserts = []
    for k in dict_prices:
        sec = dict_prices[k]
        inserts.append(sec)
    session.add_all(inserts)


@Session
async def add_market_holidays(session: AsyncSession, market_holidays: list[MarketHolidays]):
    dates = []
    for mh in market_holidays:
        dates.append(mh.holiday_date)
    response = await session.execute(select(MarketHolidays).where(MarketHolidays.holiday_date.in_(dates)))
    date_dict: dict[datetime, None] = {}
    for mh in response.scalars().all():
        date_dict[mh.holiday_date] = None

    insertable = []
    for mh in market_holidays:
        if mh.holiday_date in date_dict:
            continue
        insertable.append(mh)
    session.add_all(insertable)
