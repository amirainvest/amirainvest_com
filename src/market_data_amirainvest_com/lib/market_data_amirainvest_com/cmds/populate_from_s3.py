import asyncio
import csv
import os
import re
from decimal import Decimal
from pprint import pprint

from common_amirainvest_com.s3.client import S3
from common_amirainvest_com.s3.consts import AMIRA_SECURITIES_HISTORICAL_PRICES_BUCKET
from market_data_amirainvest_com.models.iex import HistoricalPrice
from market_data_amirainvest_com.repository import add_to_db, get_security_by_ticker_symbol


# Get all keys from S3
# Iterate Over Key history files and add prices to DB

not_found_securities = []


async def work(root_key: str):
    s3_service = S3()
    keys = re.split(r"/", root_key)
    local_filename = keys[1]
    await s3_service.download_object(
        local_filepath=local_filename, bucket=AMIRA_SECURITIES_HISTORICAL_PRICES_BUCKET, key=root_key
    )
    # Get security id by ticker symbol
    security = await get_security_by_ticker_symbol(keys[0])
    if security is None:
        not_found_securities.append(keys[0])
        return

    with open(local_filename) as f:
        historical_pricing = []
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            if row["date"] == "" or row["close"] == "":
                continue
            historical_pricing.append(
                HistoricalPrice(
                    date=row["date"],
                    close=Decimal(row["close"]),
                )
            )
        await add_to_db(security.id, historical_pricing)
    os.remove(local_filename)


async def run():
    s3_service = S3()
    root_objects = await s3_service.get_all_objects(
        AMIRA_SECURITIES_HISTORICAL_PRICES_BUCKET, prefix=None, start_after=None
    )

    cnt = 0
    root_len = 0
    params = []
    count = 0
    while root_objects is not None:
        root_len = len(root_objects) + root_len
        for root_object in root_objects:
            root_key = root_object["Key"]
            count = count + 1
            params.append(root_key)
            cnt = cnt + 1
            if len(params) == 20:
                await asyncio.gather(*(work(param) for param in params))
                await asyncio.sleep(2)
                print("Processed: {}/{}\n\n".format(cnt, root_len))
                params = []
        start_after = root_objects[len(root_objects) - 1]["Key"]
        root_objects = await s3_service.get_all_objects(
            AMIRA_SECURITIES_HISTORICAL_PRICES_BUCKET, prefix=None, start_after=start_after
        )
    if len(params) > 0:
        await asyncio.gather(*(work(param) for param in params))


if __name__ == "__main__":
    asyncio.run(run())
    pprint(not_found_securities)
