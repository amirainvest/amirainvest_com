import time
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from common_amirainvest_com.schemas.schema import Securities, SecurityPrices
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from common_amirainvest_com.utils.decorators import Session
from market_data_amirainvest_com.iex import get_stock_quote_prices
from market_data_amirainvest_com.models.iex import StockQuote
from market_data_amirainvest_com.repository import get_securities, group_securities


@Session
async def run(session: AsyncSession):
    securities = await get_securities()  # TODO swap this logic out with something else
    grouped_securities = group_securities(securities, 100)
    for group in grouped_securities:
        symbols = [sec.ticker_symbol for sec in group]
        quotes = await get_stock_quote_prices(symbols)
        securities_prices = []
        for quote in quotes:
            security_id = get_security_id(securities, quote)
            if quote.latestUpdate is None or quote.latestUpdate == 0:
                continue
            price_time = datetime.fromtimestamp(quote.latestUpdate / 1000)
            securities_prices.append(
                SecurityPrices(security_id=security_id, price=quote.latestPrice, price_time=price_time)
            )
        session.add_all(securities_prices)
        securities_prices = []
        time.sleep(1)


def get_security_id(securities: list[Securities], quote: StockQuote) -> int:
    for sec in securities:
        if sec.ticker_symbol == quote.symbol:
            return sec.id


def handler(event, context):
    run_async_function_synchronously(run)
