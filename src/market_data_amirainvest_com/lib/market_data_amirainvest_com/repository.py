import csv
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.s3.client import S3
from common_amirainvest_com.s3.consts import AMIRA_SECURITIES_HISTORICAL_PRICES_BUCKET
from common_amirainvest_com.schemas.schema import Securities, SecurityPrices
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

    file_name = f"{symbol}/{symbol}-{year}.csv"
    with open(file_name, "w", encoding="UTF-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    s3 = S3()
    await s3.upload_file(file_name, AMIRA_SECURITIES_HISTORICAL_PRICES_BUCKET, file_name)


@Session
async def _security_price_time_exists(session: AsyncSession, security_id: int, security_time: datetime) -> bool:
    response = await session.execute(
        select(SecurityPrices).where(SecurityPrices.id == security_id, SecurityPrices.price_time == security_time)
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
    # TODO: Maybe we check to see if a security price already exists before adding it as we have a UC on
    #   security_id and time?
    # Do a select where in and get all dates with that security id that exist in our array, iterate through and ignore..

    security_prices = []
    for p in historical_prices:
        if p.date is None or p.date == "":
            continue
        date = datetime.strptime(p.date, "%Y-%m-%d")
        security_prices.append(
            SecurityPrices(
                security_id=security_id,
                price=p.fClose,  # fClose = Fully Adjusted Close, close is split adjusted and uClose is unadjusted close
                price_time=date,
            )
        )
    session.add_all(security_prices)


@Session
async def get_securities(session: AsyncSession) -> list[Securities]:
    response = await session.execute(select(Securities))
    return response.scalars().all()


@Session
async def get_securities_collect_true(session: AsyncSession) -> list[Securities]:
    response = await session.execute(select(Securities).where(Securities.collect == True))  # noqa: E712
    return response.scalars().all()


@Session
async def add_securities_prices(session: AsyncSession, security_prices: list[SecurityPrices]):
    session.add_all(security_prices)
