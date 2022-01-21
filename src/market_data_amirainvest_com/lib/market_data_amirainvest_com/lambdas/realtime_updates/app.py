import asyncio
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from common_amirainvest_com.schemas.schema import Securities, SecurityPrices
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from common_amirainvest_com.utils.decorators import Session
from market_data_amirainvest_com.iex import get_stock_quote_prices
from market_data_amirainvest_com.repository import get_securities_collect_true, group_securities


@Session
async def run(session: AsyncSession):
    securities = await get_securities_collect_true()
    grouped_securities = group_securities(securities, 100)
    for group in grouped_securities:
        symbols = []
        for sec in group:
            if sec.ticker_symbol is None or sec.ticker_symbol == "":
                continue
            symbols.append(sec.ticker_symbol)

        quotes = await get_stock_quote_prices(symbols)
        securities_prices = []
        for quote in quotes:
            if quote.symbol is None or quote.symbol == "":
                continue

            security_id = get_security_id(securities, quote.symbol)
            if security_id == -1:
                # TODO: Log here that we didnt find the security.... that we just fetched....
                continue
            if quote.latestUpdate is None:
                continue
            price_time = datetime.fromtimestamp(quote.latestUpdate / 1000)
            securities_prices.append(
                SecurityPrices(security_id=security_id, price=quote.latestPrice, price_time=price_time)
            )
        session.add_all(securities_prices)
        await asyncio.sleep(1)


def get_security_id(securities: list[Securities], symbol: str) -> int:
    for sec in securities:
        if sec.ticker_symbol == symbol and sec.id is not None:
            return sec.id
    return -1


def handler(event, context):
    run_async_function_synchronously(run)
