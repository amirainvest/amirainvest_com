"""
We want to build up the holdings account per day for the last two years and all future years
1. Take current holdings
2. Take transaction history
3. Compute each day holdings substituted with IEX prices(for the most part)

Not all accounts have a line-item for cash

We can check that each account has either a depository or a cash position?
"""
from common_amirainvest_com.utils.decorators import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from common_amirainvest_com.schemas.schema import (
    MarketHolidays
)


@Session
def get_market_holidays(session: AsyncSession) -> dict[MarketHolidays, None]:
    response = await session.execute(select(MarketHolidays))

    holiday_dict = {}
    for holiday in response.scalars().all():
        holiday_dict[holiday.date] = None
    return holiday_dict
