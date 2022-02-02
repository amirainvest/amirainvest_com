import argparse
import asyncio

from common_amirainvest_com.s3.client import S3
from common_amirainvest_com.s3.consts import AMIRA_SECURITIES_HISTORICAL_PRICES_BUCKET
from common_amirainvest_com.schemas.schema import Securities
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from market_data_amirainvest_com.iex import get_historical_prices, HistoricalPriceEnum
from random import randrange
from market_data_amirainvest_com.repository import add_to_db, add_to_s3, get_securities, group_securities


# TODO: In the mean-time we should probably just keep this at 3 months...?
# TODO: Check to see if empty / report error??
# TODO: Should we do anything with timeouts / retries?
# TODO: Maybe we write exception err to a file or something...? store all issues in an array, write to file, re-process


async def work(security: Securities, year: int):
    try:
        await asyncio.sleep(randrange(10))
        historical_pricing = await get_historical_prices(
            security.ticker_symbol, HistoricalPriceEnum.OneYear, f"{year}0101".upper()
        )

        # IS this because it failed.... or because it doesnt exist....!
        if len(historical_pricing) <= 0:
            print("NO PRICING FOR ", security.ticker_symbol)
            return

        await add_to_s3(historical_pricing, security.ticker_symbol, year)
        # await add_to_db(security.id, historical_pricing)
    except Exception as err:
        print(err)


async def prune_securities_list(year: int, securities: list[Securities]) -> list[Securities]:
    s3 = S3()
    all_objects = await s3.get_all_objects(AMIRA_SECURITIES_HISTORICAL_PRICES_BUCKET)
    current_securities = {}
    for obj in all_objects:
        current_securities[obj.key] = {}

    sec_list = []
    for sec in securities:
        security_key = f"{sec.ticker_symbol}/{sec.ticker_symbol}-{year}.csv"
        if security_key in current_securities:
            continue
        sec_list.append(sec)

    return sec_list


async def run(year: int):
    securities = await get_securities()
    pruned_securities_list = await prune_securities_list(year, securities)
    grouped_securities = group_securities(pruned_securities_list, 25)

    for group in grouped_securities:
        await asyncio.gather(*(work(params, year) for params in group))
        await asyncio.sleep(10)


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

    for year in range(start_year, end_year + 1):
        run_async_function_synchronously(run, year)
