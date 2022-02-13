import asyncio
import datetime

from common_amirainvest_com.schemas.schema import Securities, SecurityPrices
from market_data_amirainvest_com.iex import get_stock_quote_prices
from market_data_amirainvest_com.repository import bulk_upsert_security_prices, get_securities, group_securities


async def run():
    securities = await get_securities()
    grouped_securities = group_securities(securities, 100)
    for group in grouped_securities:
        symbols: list[str] = []
        securities_dict: [str, Securities] = {}
        for sec in group:
            symbols.append(sec.ticker_symbol)
            securities_dict[sec.ticker_symbol] = sec
        eod_stock_prices = await get_stock_quote_prices(symbols)

        insertable = []
        dt = datetime.datetime.utcnow()
        dt = dt.replace(hour=21, minute=0, second=0, microsecond=0)
        for eod_stock_price in eod_stock_prices:
            new_sec = securities_dict[eod_stock_price.symbol]
            insertable.append(SecurityPrices(security_id=new_sec.id, price=eod_stock_price.latestPrice, price_time=dt))
        await bulk_upsert_security_prices(insertable)
        await asyncio.sleep(5)


async def handler(event, context):
    asyncio.run(run())
