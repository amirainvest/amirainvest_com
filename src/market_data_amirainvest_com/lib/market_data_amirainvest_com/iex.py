import enum
from typing import Union

import httpx

from common_amirainvest_com.utils.consts import IEX_SECRET, IEX_URL
from market_data_amirainvest_com.models.iex import Company, HistoricalPrice, StockQuote, Symbol


class HistoricalPriceEnum(enum.Enum):
    Max = "max"
    TwoYear = "2y"
    OneYear = "1y"
    YearToDate = "ytd"
    SixMonths = "6m"
    ThreeMonths = "3m"
    OneMonth = "1m"
    OneMonth30MinuteIntervals = "3mm"
    FiveDays = "5d"
    FiveDays10MinuteIntervals = "5dm"
    OneDay = "dynamic"  # 1d or 1m data depending on day or week and time of time


# Returns historical prices for last 15 years
# Can pass in an enum or a specific date in YYYYMMDD format
async def get_historical_prices(symbol: str, range: Union[HistoricalPriceEnum, str]) -> list[HistoricalPrice]:
    range_value = range
    if type(range) == HistoricalPriceEnum:
        range_value = range.value

    request_url = f"{IEX_URL}/stock/{symbol}/chart/{range_value}?token={IEX_SECRET}"
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20)
        validate_response(r.status_code, r.text)
        response = r.json()
        arr = []
        for item in response:
            arr.append(HistoricalPrice(**item))
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


class IEXError(Exception):
    pass


# TODO: Text can sometime can be blank and we should probably hard-code
#   some error messages and return those
def validate_response(status_code: int, content: str):
    if status_code >= 400:
        raise IEXError(content)
