import asyncio
import datetime
from typing import List

from common_amirainvest_com.utils.decorators import Session
from sqlalchemy.ext.asyncio import AsyncSession
from common_amirainvest_com.utils.consts import IEX_SECRET
from common_amirainvest_com.schemas.schema import Securities, SecurityPrices
from common_amirainvest_com.utils.logger import log
from market_data_amirainvest_com.iex import get_stock_quote_prices
from market_data_amirainvest_com.models.iex import StockQuote
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


async def _get_security_prices(stock_quotes: List[StockQuote], securities: List[Securities]) -> List[SecurityPrices]:
    securities_prices = []
    for stock_quote in stock_quotes:
        if stock_quote.symbol is None or stock_quote.symbol == "" or stock_quote.latestUpdate is None:
            continue
        security_id = get_security_id(securities, stock_quote.symbol)
        if security_id == -1:
            continue
        price_time = round_time_to_minute_floor(datetime.datetime.fromtimestamp(stock_quote.latestUpdate / 1000))
        if await _security_price_time_exists(security_id, price_time):
            continue
        securities_prices.append(
            SecurityPrices(security_id=security_id, price=stock_quote.latestPrice, price_time=price_time)
        )
    return securities_prices


@Session
async def remove(session: AsyncSession):
    await session.close()


async def run():
    try:
        print("HI!!! ", IEX_SECRET)
        securities = await get_securities_collect_true()
        for sec in securities:
            print(sec.ticker_symbol)
        # grouped_securities = group_securities(securities, 100)
        # for group in grouped_securities:
        #     symbols = _group_just_symbols(group)
        #     quotes = await get_stock_quote_prices(symbols)
        #     securities_prices = await _get_security_prices(quotes, securities)
        #     await _add_securities_prices(securities_prices)
        #     await asyncio.sleep(1)
        await remove()
    except Exception as err:
        log.exception(err)
        raise err


def round_time_to_minute_floor(tm: datetime.datetime) -> datetime.datetime:
    return tm - datetime.timedelta(minutes=tm.minute % 1, seconds=tm.second, microseconds=tm.microsecond)


def get_security_id(securities: list[Securities], symbol: str) -> int:
    for sec in securities:
        if sec.ticker_symbol == symbol and sec.id is not None:
            return sec.id
    return -1


def handler(event, context):
    print("HERE!>!>")
    asyncio.run(run())
    print("<!<!<! HERE")
