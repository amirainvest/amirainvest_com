import argparse
import asyncio
import time

from common_amirainvest_com.s3.client import S3
from common_amirainvest_com.s3.consts import AMIRA_SECURITIES_HISTORICAL_PRICES_BUCKET
from common_amirainvest_com.schemas.schema import Securities
from market_data_amirainvest_com.iex import get_historical_prices, HistoricalPriceEnum
from market_data_amirainvest_com.repository import add_to_db, add_to_s3, get_securities, group_securities


# TODO: In the mean-time we should probably just keep this at 3 months...?
# TODO: Check to see if empty / report error??
# TODO: Should we do anything with timeouts / retries?
# TODO: Maybe we write exception err to a file or something...? store all issues in an array, write to file, re-process


async def work(security: Securities, year: int):
    try:
        s3 = S3()
        key = f"{security.ticker_symbol}/{security.ticker_symbol}-{year}.csv"
        if s3.validate_object_exists(AMIRA_SECURITIES_HISTORICAL_PRICES_BUCKET, key):
            return

        historical_pricing = await get_historical_prices(
            security.ticker_symbol, HistoricalPriceEnum.OneYear, f"{year}0101".upper()
        )
        await add_to_s3(historical_pricing, security.ticker_symbol, year)
        await add_to_db(security.id, historical_pricing)
    except Exception as err:
        print(err)


async def run(year: int):
    securities = await get_securities()
    grouped_securities = group_securities(securities)

    for group in grouped_securities:
        await asyncio.gather(*(work(params, year) for params in group))
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest All Securities By Year Range")
    parser.add_argument(
        "--start-year",
        dest="start_year",
        type=int,
        help="Starting year of the range to ingest for all historical prices.",
    )
    parser.add_argument(
        "--end-year", dest="end_year", type=int, help="Ending year of the range to ingest for all historical prices."
    )
    args = vars(parser.parse_args())
    start_year = args["start_year"]
    end_year = args["end_year"]

    if start_year is None:
        print("No start year set")
        exit(1)

    if end_year is None:
        print("No end year set")
        exit(1)

    # for year in range(start_year, end_year + 1):
    #     run_async_function_synchronously(run)
