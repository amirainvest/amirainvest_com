import asyncio
from common_amirainvest_com.schemas.schema import MarketHolidays
from market_data_amirainvest_com.models.iex import MarketHoliday, MarketHolidayDirection
from market_data_amirainvest_com.iex import get_market_holidays
from market_data_amirainvest_com.repository import add_market_holidays


async def run():
    holidays = await get_market_holidays(MarketHolidayDirection.last)
    last_holidays = []
    for lmh in holidays:
        last_holidays.append(
            MarketHolidays(
                holiday_date=lmh.date,
                settlement_date=lmh.settlementDate
            )
        )
    await add_market_holidays(last_holidays)

    holidays = await get_market_holidays(MarketHolidayDirection.next)
    next_holidays = []
    for lmh in holidays:
        next_holidays.append(
            MarketHolidays(
                holiday_date=lmh.date,
                settlement_date=lmh.settlementDate
            )
        )
    await add_market_holidays(next_holidays)


def handler(event, context):
    asyncio.run(run())


handler(None, None)
