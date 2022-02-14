from typing import Union

import httpx

from common_amirainvest_com.iex.exceptions import IEXException
from common_amirainvest_com.iex.model import (
    Company,
    HistoricalPrice,
    HistoricalPriceEnum,
    HistoricalPriceFiveDay,
    IntradayPrice,
    MarketHoliday,
    MarketHolidayDirection,
    StockQuote,
    Symbol,
)
from common_amirainvest_com.utils.consts import IEX_SECRET, IEX_URL


async def get_historical_five_day_pricing(symbol: str) -> list[HistoricalPriceFiveDay]:
    request_url = f"{IEX_URL}/stock/{symbol}/chart/5dm?token={IEX_SECRET}&chartCloseOnly=true"

    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20)
        validate_response(r.status_code, r.text)
        response = r.json()
        arr = []
        for item in response:
            arr.append(HistoricalPriceFiveDay(**item))
        return arr


# TODO ... Need to fix/clean-up... IEX passes a different JSON structure PER range date... from the same API endpoint
# Returns historical prices for last 15 years
# Can pass in an enum or a specific date in YYYYMMDD format
async def get_historical_prices(symbol: str, range_: Union[HistoricalPriceEnum, str], date="") -> list[HistoricalPrice]:
    range_value = range_
    if type(range_) == HistoricalPriceEnum:
        range_value = range_.value

    # TODO the token should be query param in client.get()
    request_url = f"{IEX_URL}/stock/{symbol}/chart/{range_value}?token={IEX_SECRET}&chartCloseOnly=true"
    if date != "":
        request_url = f"{request_url}&range={date}"

    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20)
        validate_response(r.status_code, r.text)
        response = r.json()
        arr = []
        for item in response:
            arr.append(HistoricalPrice(**item))
        return arr


async def get_intraday_prices(symbol: str) -> list[IntradayPrice]:
    request_url = f"{IEX_URL}/stock/{symbol}/intraday-prices?token={IEX_SECRET}"
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20.0)
        validate_response(r.status_code, r.text)
        response = r.json()
        arr = []
        for item in response:
            arr.append(IntradayPrice(**item))
        return arr


async def get_stock_quote(symbol: str) -> StockQuote:
    request_url = f"{IEX_URL}/stock/{symbol}/quote?token={IEX_SECRET}"
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20.0)
        validate_response(r.status_code, r.text)
        response = r.json()
        return StockQuote(**response)


async def get_stock_quote_prices(symbols: list[str]) -> list[StockQuote]:
    symbol_list = ",".join(symbols)
    request_url = f"{IEX_URL}/stock/market/batch?symbols={symbol_list}&types=quote&token={IEX_SECRET}"
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20.0)
        validate_response(r.status_code, r.text)
        response = r.json()
        arr = []
        for key in response:
            quote = response[key]["quote"]
            arr.append(StockQuote(**quote))
        return arr


async def get_company_info(symbol: str) -> Company:
    request_url = f"{IEX_URL}/stock/{symbol}/company?token={IEX_SECRET}"
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20.0)
        validate_response(r.status_code, r.text)
        response = r.json()
        return Company(**response)


async def get_supported_securities_list() -> list[Symbol]:
    request_url = f"{IEX_URL}/ref-data/symbols?token={IEX_SECRET}"
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20.0)
        validate_response(r.status_code, r.text)
        response = r.json()
        arr = []
        for item in response:
            arr.append(Symbol(**item))
        return arr


async def get_market_holidays(holiday_direction: MarketHolidayDirection) -> list[MarketHoliday]:
    request_url = f"{IEX_URL}/ref-data/us/dates/holiday/{holiday_direction.value}?token={IEX_SECRET}"
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20.0)
        validate_response(r.status_code, r.text)
        response = r.json()
        arr = []
        for item in response:
            arr.append(MarketHoliday(**item))
        return arr


# TODO: Text can sometime can be blank and we should probably hard-code
#   some error messages and return those
def validate_response(status_code: int, content: str):
    if status_code >= 400:
        raise IEXException(content)