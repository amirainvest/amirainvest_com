import asyncio
import datetime
from typing import List

from common_amirainvest_com.iex.client import get_stock_quote_prices
from common_amirainvest_com.iex.model import StockQuote
from common_amirainvest_com.schemas.schema import Securities, SecurityPrices
from common_amirainvest_com.utils.consts import async_engine
from common_amirainvest_com.utils.logger import log
from market_data_amirainvest_com.repository import (
    _add_securities_prices,
    _security_price_time_exists,
    get_securities_collect_true,
    group_securities,
)


def _group_just_symbols(securities: List[Securities]) -> List[str]:
    symbols = []
    for sec in securities:
        symbols.append(sec.ticker_symbol)
    return symbols


async def _get_security_prices(
    stock_quotes: List[StockQuote], securities: List[Securities], current_minute: datetime.datetime
) -> List[SecurityPrices]:
    securities_prices = []
    for stock_quote in stock_quotes:
        if stock_quote.symbol is None or stock_quote.symbol == "" or stock_quote.latestUpdate is None:
            continue
        security_id = get_security_id(securities, stock_quote.symbol)
        if security_id == -1:
            continue
        stock_price_time = round_time_to_minute_floor(datetime.datetime.fromtimestamp(stock_quote.latestUpdate / 1000))

        # TODO should be one query to check...., or we should should get a bulk load of all stocks
        #   with their price times available.
        if await _security_price_time_exists(security_id, stock_price_time):
            if await _security_price_time_exists(security_id, current_minute):
                continue
            stock_price_time = current_minute
        securities_prices.append(
            SecurityPrices(security_id=security_id, price=stock_quote.latestPrice, price_time=stock_price_time)
        )
    return securities_prices


async def run():
    try:
        securities = await get_securities_collect_true()
        grouped_securities = group_securities(securities, 100)
        current_minute = round_time_to_minute_floor(datetime.datetime.now())

        # TODO watch for a "To many requests" exception and retry....
        for group in grouped_securities:
            symbols = _group_just_symbols(group)
            quotes = await get_stock_quote_prices(symbols)

            securities_prices = await _get_security_prices(quotes, securities, current_minute)
            await _add_securities_prices(securities_prices)
            await asyncio.sleep(1)
    except Exception as err:
        log.exception(err)
        raise err
    finally:
        await async_engine.dispose()


def round_time_to_minute_floor(tm: datetime.datetime) -> datetime.datetime:
    return tm - datetime.timedelta(minutes=tm.minute % 1, seconds=tm.second, microseconds=tm.microsecond)


def get_security_id(securities: list[Securities], symbol: str) -> int:
    for sec in securities:
        if sec.ticker_symbol == symbol and sec.id is not None:
            return sec.id
    return -1


def handler(event, context):
    asyncio.run(run())
