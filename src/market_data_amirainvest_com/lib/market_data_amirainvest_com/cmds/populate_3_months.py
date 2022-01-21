import asyncio
import time

from common_amirainvest_com.schemas.schema import Securities
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from market_data_amirainvest_com.iex import get_historical_prices, HistoricalPriceEnum
from market_data_amirainvest_com.repository import add_to_db, get_securities, group_securities


async def work(security: Securities):
    try:
        historical_prices = await get_historical_prices(security.ticker_symbol, HistoricalPriceEnum.ThreeMonths)
        await add_to_db(security.id, historical_prices)
    except Exception:
        pass


async def run():
    securities = await get_securities()
    grouped_securities = group_securities(securities, 100)

    # Processes Securities in Groups of 100
    for group in grouped_securities:
        await asyncio.gather(*(work(security) for security in group))
        time.sleep(1)


if __name__ == "__main__":
    run_async_function_synchronously(run)
