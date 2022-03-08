import asyncio
import datetime

from common_amirainvest_com.iex.client import get_stock_quote_prices
from common_amirainvest_com.schemas.schema import Securities, SecurityInformation, SecurityPrices
from common_amirainvest_com.utils.consts import async_engine
from common_amirainvest_com.utils.logger import log
from market_data_amirainvest_com.repository import (
    bulk_upsert_security_information,
    bulk_upsert_security_prices,
    get_securities,
    group_securities,
)


async def run():
    try:
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
            insert_security_information = []
            dt = datetime.datetime.utcnow()
            dt = dt.replace(hour=21, minute=0, second=0, microsecond=0)
            for esp in eod_stock_prices:
                new_sec = securities_dict[esp.symbol]
                insertable.append(SecurityPrices(security_id=new_sec.id, price=esp.latestPrice, price_time=dt))
                insert_security_information.append(
                    SecurityInformation(
                        security_id=new_sec.id,
                        average_total_volume=esp.avgTotalVolume,
                        change=esp.change,
                        change_percentage=esp.changePercent,
                        close=esp.close,
                        close_source=esp.closeSource,
                        close_time=esp.closeTime / 1000 if esp.closeTime is not None else None,
                        currency=esp.currency,
                        delayed_price=esp.delayedPrice,
                        delayed_price_time=esp.delayedPriceTime / 1000 if esp.delayedPriceTime is not None else None,
                        extended_change=esp.extendedChange,
                        extended_change_percentage=esp.extendedChangePercent,
                        extended_price=esp.extendedPrice,
                        extended_price_time=esp.extendedPriceTime / 1000 if esp.extendedPriceTime is not None else None,
                        high=esp.high,
                        high_source=esp.highSource,
                        high_time=esp.highTime / 1000 if esp.highTime is not None else None,
                        iex_ask_price=esp.iexAskPrice,
                        iex_bid_price=esp.iexBidPrice,
                        iex_close=esp.iexClose,
                        iex_close_time=esp.iexCloseTime / 1000 if esp.iexCloseTime is not None else None,
                        iex_last_updated=esp.iexLastUpdated / 1000 if esp.iexLastUpdated is not None else None,
                        iex_market_percentage=esp.iexMarketPercent,
                        iex_open=esp.iexOpen,
                        iex_open_time=esp.iexOpenTime / 1000 if esp.iexOpenTime is not None else None,
                        iex_realtime_price=esp.iexRealtimePrice,
                        iex_real_time_size=esp.iexRealtimeSize,
                        iex_volume=esp.iexVolume,
                        last_trade_time=esp.lastTradeTime / 1000 if esp.lastTradeTime is not None else None,
                        latest_price=esp.latestPrice,
                        latest_source=esp.latestSource,
                        latest_time=esp.latestTime,
                        latest_update=esp.latestUpdate / 1000 if esp.latestUpdate is not None else None,
                        latest_volume=esp.latestVolume,
                        low=esp.low,
                        low_source=esp.lowSource,
                        low_time=esp.lowTime / 1000 if esp.lowTime is not None else None,
                        market_cap=esp.marketCap,
                        odd_lot_delayed_price=esp.oddLotDelayedPrice,
                        odd_lot_delayed_price_time=esp.oddLotDelayedPriceTime / 1000
                        if esp.oddLotDelayedPriceTime is not None
                        else None,
                        open=esp.open,
                        open_time=esp.openTime / 1000 if esp.openTime is not None else None,
                        open_source=esp.openSource,
                        pe_ratio=esp.peRatio,
                        previous_close=esp.previousClose,
                        previous_volume=esp.previousVolume,
                        volume=esp.volume,
                        week_high_52=esp.week52High,
                        week_low_52=esp.week52Low,
                        ytd_change=esp.ytdChange,
                    )
                )
            await bulk_upsert_security_prices(insertable)
            await bulk_upsert_security_information(insert_security_information)
            await asyncio.sleep(1)
    except Exception as err:
        log.exception(err)
        raise err
    finally:
        await async_engine.dispose()


def handler(event, context):
    asyncio.run(run())


handler()
