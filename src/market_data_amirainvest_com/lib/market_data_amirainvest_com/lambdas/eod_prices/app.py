import time

# from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
# from market_data_amirainvest_com.iex import get_stock_quote_prices
from market_data_amirainvest_com.repository import get_securities, group_securities


# Get all quotes
# Insert prices
# Update open/close on security open for security....
# Run once in the AM / Once in the PM


async def run():
    securities = await get_securities()
    grouped_securities = group_securities(securities, 100)

    for group in grouped_securities:
        # Get all quotes
        # Insert prices
        # Update open/close on security open for security....
        # Run once in the AM / Once in the PM
        time.sleep(1)


def handler(event, context):
    pass
