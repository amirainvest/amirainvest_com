import asyncio
import csv
from datetime import datetime
from decimal import Decimal

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from common_amirainvest_com.schemas.schema import Securities, SecurityPrices
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_security(session: AsyncSession) -> Row:
    security = {
        "collect": False,
        "is_benchmark": False,
        "human_readable_name": "Two-Year Treasury Yield",
        "ticker_symbol": "US02Y",
        "close_price": 0,
        "name": "Two-Year Treasury Yield",
        "open_price": 0,
    }
    return (await session.execute(insert(Securities).values(**security).returning(Securities))).one()


@Session
async def insert_security_prices(session: AsyncSession, security_prices: list):
    group = []
    for item in security_prices:
        group.append(item)
        if len(group) == 1000:
            await session.execute(insert(SecurityPrices).values(group).on_conflict_do_nothing())
            await session.commit()
            group = []
    await session.execute(insert(SecurityPrices).values(group).on_conflict_do_nothing())
    await session.commit()


async def run():
    # CREATE Security US02Y
    security = await create_security()

    with open("free-market-rates.csv") as f:
        prices = []
        reader = csv.DictReader(f)
        for row in reader:
            dt = datetime.strptime(row["DATE"], "%Y-%m-%d")
            dt = dt.replace(hour=21, minute=0, second=0, microsecond=0, tzinfo=None)
            price_str = row["DGS2"]
            if price_str == ".":
                price = prices[len(prices) - 1]["price"]
            else:
                price = Decimal(price_str)
            prices.append({"security_id": security.id, "price": price, "price_time": dt})
    await insert_security_prices(security_prices=prices)


if __name__ == "__main__":
    asyncio.run(run())
