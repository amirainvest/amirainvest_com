import csv
import asyncio
import time

from common_amirainvest_com.s3.consts import AMIRA_SECURITIES_HISTORICAL_PRICES_BUCKET
from common_amirainvest_com.s3.client import S3
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.schemas.schema import Securities, SecurityPrices
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from market_data_amirainvest_com.iex import get_historical_prices, HistoricalPriceEnum, HistoricalPrice
from datetime import date


# TODO: Rewrite script to consider pulling in current data, if exists, then updating that data with the latest date range
#   we should be able to specify how far back to go and at which starting point


@Session
async def get_securities(session: AsyncSession) -> list[Securities]:
    response = await session.execute(select(Securities))
    return response.scalars().all()


def group_securities(securities: list[Securities]) -> list[list[Securities]]:
    grouping = []
    sub_group = []
    for security in securities:
        sub_group.append(security)
        if len(sub_group) >= 100:
            grouping.append(sub_group)
            sub_group = []

    if len(sub_group) > 0:
        grouping.append(sub_group)
    return grouping


async def add_to_s3(historical_prices: list[HistoricalPrice], symbol: str, time_range: HistoricalPriceEnum):
    headers = ['close', 'high', 'low', 'open', 'symbol', 'volume', 'id', 'key', 'date', 'updated', 'changeOverTime',
               'marketChangeOverTime', 'uOpen', 'uClose', 'uHigh', 'uLow', 'uVolume', 'fOpen', 'fClose', 'fHigh',
               'fLow', 'fVolume', 'label', 'change', 'changePercent']
    rows = []
    for p in historical_prices:
        rows.append(
            [
                p.close, p.high, p.low, p.open, p.symbol, p.volume, p.id, p.key, p.date, p.updated, p.changeOverTime,
                p.marketChangeOverTime, p.uOpen, p.uClose, p.uHigh, p.uLow, p.uVolume, p.fOpen, p.fClose, p.fHigh,
                p.fLow, p.fVolume, p.label, p.change, p.changePercent
            ]
        )
    today = date.today()
    file_name = f"historical_pricing/{symbol}-{today}-{time_range.value}.csv"
    with open(file_name, 'w', encoding='UTF-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    s3 = S3()
    await s3.upload_file(file_name, AMIRA_SECURITIES_HISTORICAL_PRICES_BUCKET, file_name)


@Session
async def add_to_db(session: AsyncSession, security_id: int, historical_prices: list[HistoricalPrice]):
    # TODO: Maybe we check to see if a security price already exists before adding it as we have a UC on
    #   security_id and time?
    security_prices = []
    for p in historical_prices:
        security_prices.append(
            SecurityPrices(
                securities_id=security_id,
                price=p.fClose,  # fClose = Fully Adjusted Close, close is split adjusted and uClose is unadjusted close
                price_time=p.date,
            )
        )
    session.add_all(security_prices)


async def work(security: Securities):
    # TODO: Try/Catch timeout here and if timed-out lets add to a retry array or write to a file to retry..?
    try:
        historical_prices = await get_historical_prices(security.ticker_symbol, HistoricalPriceEnum.ThreeMonths)
        await add_to_s3(historical_prices, security.ticker_symbol, HistoricalPriceEnum.ThreeMonths)
        await add_to_db(security.id, historical_prices)
    except TimeoutError:
        pass
    except Exception:
        pass


async def run():
    securities = await get_securities()
    grouped_securities = group_securities(securities)

    # Processes Securities in Groups of 100
    for group in grouped_securities:
        await asyncio.gather(*(work(security) for security in group))
        time.sleep(1)
