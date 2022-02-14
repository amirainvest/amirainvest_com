import asyncio

from common_amirainvest_com.schemas.schema import MarketHolidays
from market_data_amirainvest_com.iex import get_market_holidays
from market_data_amirainvest_com.models.iex import MarketHolidayDirection
from market_data_amirainvest_com.repository import add_market_holidays


async def run():
    last_holidays = await get_market_holidays(MarketHolidayDirection.last)
    next_holidays = await get_market_holidays(MarketHolidayDirection.next)
    holidays = []
    for lmh in last_holidays:
        holidays.append(MarketHolidays(date=lmh.date, settlement_date=lmh.settlementDate))
    for nmh in next_holidays:
        holidays.append(MarketHolidays(date=nmh.date, settlement_date=nmh.settlementDate))
    await add_market_holidays(holidays)


def handler(event, context):
    asyncio.run(run())
