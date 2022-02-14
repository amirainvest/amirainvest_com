import csv
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.s3.client import S3
from common_amirainvest_com.s3.consts import AMIRA_SECURITIES_HISTORICAL_PRICES_BUCKET
from common_amirainvest_com.schemas.schema import MarketHolidays, Securities, SecurityInformation, SecurityPrices
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
async def bulk_upsert_security_information(session: AsyncSession, security_information: list[SecurityInformation]):
    security_ids = []
    si_dict: dict[int, SecurityInformation] = {}
    for si in security_information:
        security_ids.append(si.security_id)
        si_dict[si.security_id] = si

    response = await session.execute(
        select(SecurityInformation).where(SecurityInformation.security_id.in_(security_ids))
    )

    for cur_si in response.scalars().all():
        si = si_dict[cur_si.security_id]
        cur_si.average_total_volume = si.average_total_volume
        cur_si.change = si.change
        cur_si.change_percentage = si.change_percentage
        cur_si.close = si.close
        cur_si.close_source = si.close_source
        cur_si.close_time = si.close_time
        cur_si.currency = si.currency
        cur_si.delayed_price = si.delayed_price
        cur_si.delayed_price_time = si.delayed_price_time
        cur_si.extended_change = si.extended_change
        cur_si.extended_change_percentage = si.extended_change_percentage
        cur_si.extended_price = si.extended_price
        cur_si.extended_price_time = si.extended_price_time
        cur_si.high = si.high
        cur_si.high_source = si.high_source
        cur_si.high_time = si.high_time
        cur_si.iex_ask_price = si.iex_ask_price
        cur_si.iex_ask_size = si.iex_ask_size
        cur_si.iex_bid_price = si.iex_bid_price
        cur_si.iex_bid_size = si.iex_bid_size
        cur_si.iex_close = si.iex_close
        cur_si.iex_close_time = si.iex_close_time
        cur_si.iex_last_updated = si.iex_last_updated
        cur_si.iex_market_percentage = si.iex_market_percentage
        cur_si.iex_open = si.iex_open
        cur_si.iex_open_time = si.iex_open_time
        cur_si.iex_realtime_price = si.iex_realtime_price
        cur_si.iex_real_time_size = si.iex_real_time_size
        cur_si.iex_volume = si.iex_volume
        cur_si.last_trade_time = si.last_trade_time
        cur_si.latest_price = si.latest_price
        cur_si.latest_source = si.latest_source
        cur_si.latest_time = si.latest_time
        cur_si.latest_update = si.latest_update
        cur_si.latest_volume = si.latest_volume
        cur_si.low = si.low
        cur_si.low_source = si.low_source
        cur_si.low_time = si.low_time
        cur_si.market_cap = si.market_cap
        cur_si.odd_lot_delayed_price = si.odd_lot_delayed_price
        cur_si.odd_lot_delayed_price_time = si.odd_lot_delayed_price_time
        cur_si.open = si.open
        cur_si.open_time = si.open_time
        cur_si.open_source = si.open_source
        cur_si.pe_ratio = si.pe_ratio
        cur_si.previous_close = si.previous_close
        cur_si.previous_volume = si.previous_volume
        cur_si.volume = si.volume
        cur_si.week_high_52 = si.week_high_52
        cur_si.week_low_52 = si.week_low_52
        cur_si.ytd_change = si.ytd_change
        del si_dict[cur_si.security_id]
    await session.flush()

    inserts = []
    for si_key in si_dict:
        si = si_dict[si_key]
        inserts.append(si)
    session.add_all(inserts)


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
    await session.flush()

    inserts = []
    for k in dict_prices:
        sec = dict_prices[k]
        inserts.append(sec)
    session.add_all(inserts)


@Session
async def add_market_holidays(session: AsyncSession, market_holidays: list[MarketHolidays]):
    dates = []
    for mh in market_holidays:
        dates.append(mh.date)
    response = await session.execute(select(MarketHolidays).where(MarketHolidays.date.in_(dates)))
    date_dict: dict[datetime, None] = {}
    for mh in response.scalars().all():
        date_dict[mh.date] = None

    insertable = []
    for mh in market_holidays:
        if mh.date in date_dict:
            continue
        insertable.append(mh)
    session.add_all(insertable)
