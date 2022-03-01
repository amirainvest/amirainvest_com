import asyncio

from common_amirainvest_com.iex.client import get_market_holidays
from common_amirainvest_com.iex.model import MarketHolidayDirection
from common_amirainvest_com.schemas.schema import MarketHolidays
from market_data_amirainvest_com.repository import add_market_holidays
from common_amirainvest_com.utils.consts import async_engine
from common_amirainvest_com.utils.logger import log


async def run():
    try:
        last_holidays = await get_market_holidays(MarketHolidayDirection.last)
        next_holidays = await get_market_holidays(MarketHolidayDirection.next)
        holidays = []
        for lmh in last_holidays:
            holidays.append(MarketHolidays(date=lmh.date, settlement_date=lmh.settlementDate))
        for nmh in next_holidays:
            holidays.append(MarketHolidays(date=nmh.date, settlement_date=nmh.settlementDate))
        await add_market_holidays(holidays)
    except Exception as err:
        log.exception(err)
        raise err
    finally:
        await async_engine.dispose()


def handler(event, context):
    asyncio.run(run())
