from typing import Union

import httpx
import pydantic

from common_amirainvest_com.iex.exceptions import IEXException
from common_amirainvest_com.iex.model import (
    Company,
    CompanyQuoteLogo,
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
    request_url = f"{IEX_URL}/stock/{symbol}/chart/5dm"
    query_strings = {"token": IEX_SECRET, "chartCloseOnly": True}
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20, params=query_strings)
        validate_response(r.status_code, r.text)
        response = r.json()
        return [HistoricalPriceFiveDay.parse_obj(item) for item in response]


# TODO ... Need to fix/clean-up... IEX passes a different JSON structure PER range date... from the same API endpoint
# Returns historical prices for last 15 years
# Can pass in an enum or a specific date in YYYYMMDD format
async def get_historical_prices(symbol: str, range_: Union[HistoricalPriceEnum, str], date="") -> list[HistoricalPrice]:
    range_value = range_
    if type(range_) == HistoricalPriceEnum:
        range_value = range_.value

    request_url = f"{IEX_URL}/stock/{symbol}/chart/{range_value}"
    query_strings = {"token": IEX_SECRET, "chartCloseOnly": True}
    if date != "":
        query_strings["range"] = date

    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20, params=query_strings)
        validate_response(r.status_code, r.text)
        response = r.json()
        return [HistoricalPrice.parse_obj(item) for item in response]


async def get_intraday_prices(symbol: str, iex_prices_when_null: bool = True) -> list[IntradayPrice]:
    request_url = f"{IEX_URL}/stock/{symbol}/intraday-prices"
    query_strings = {"token": IEX_SECRET, "chartIEXWhenNull": iex_prices_when_null}
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20.0, params=query_strings)
        validate_response(r.status_code, r.text)
        response = r.json()
        return [IntradayPrice.parse_obj(item) for item in response]


async def get_stock_quote(symbol: str) -> StockQuote:
    request_url = f"{IEX_URL}/stock/{symbol}/quote"
    query_strings = {"token": IEX_SECRET}
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20.0, params=query_strings)
        validate_response(r.status_code, r.text)
        response = r.json()
        return StockQuote.parse_obj(response)


async def get_stock_quote_prices(symbols: list[str]) -> list[StockQuote]:
    request_url = f"{IEX_URL}/stock/market/batch"
    symbol_list = ",".join(symbols)
    query_strings = {"token": IEX_SECRET, "types": "quote", "symbols": symbol_list}
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20.0, params=query_strings)
        validate_response(r.status_code, r.text)
        response = r.json()
        res = []
        for key in response:
            try:
                res.append(StockQuote.parse_obj(response[key]["quote"]))
            except pydantic.ValidationError:
                continue
        return res


async def get_company_info(symbol: str) -> Company:
    request_url = f"{IEX_URL}/stock/{symbol}/company"
    query_strings = {"token": IEX_SECRET}
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20.0, params=query_strings)
        validate_response(r.status_code, r.text)
        response = r.json()
        return Company.parse_obj(response)


async def get_company_quote_logo_bulk(symbols: list[str]) -> list[CompanyQuoteLogo]:
    request_url = f"{IEX_URL}/stock/market/batch"
    query_strings = {"token": IEX_SECRET, "symbols": ",".join(symbols), "types": "company,logo,quote"}
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20.0, params=query_strings)
        validate_response(r.status_code, r.text)
        response = r.json()

        companies = []
        for key, val in response.items():
            company = {}
            if "company" in val:
                company = val["company"]

            quote = {}
            if "quote" in val:
                quote = val["quote"]
            obj = {**quote, **company}

            c = CompanyQuoteLogo.parse_obj(obj)
            if "logo" in val:
                if "url" in val:
                    logo = val["logo"]["url"]
                    c.logo_url = logo

            companies.append(c)
        return companies


async def get_company_bulk(symbols: list[str]) -> list[Company]:
    request_url = f"{IEX_URL}/stock/market/batch"
    query_strings = {"token": IEX_SECRET, "symbols": ",".join(symbols), "types": "company"}
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20.0, params=query_strings)
        validate_response(r.status_code, r.text)
        response = r.json()

        companies = []
        for key, val in response.items():
            company = val["company"]
            c = Company.parse_obj(company)
            companies.append(c)
        return companies


async def get_supported_securities_list() -> list[Symbol]:
    request_url = f"{IEX_URL}/ref-data/symbols"
    query_strings = {"token": IEX_SECRET}
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20.0, params=query_strings)
        validate_response(r.status_code, r.text)
        response = r.json()
        return [Symbol.parse_obj(item) for item in response]


async def get_market_holidays(holiday_direction: MarketHolidayDirection) -> list[MarketHoliday]:
    request_url = f"{IEX_URL}/ref-data/us/dates/holiday/{holiday_direction.value}/365"
    query_strings = {"token": IEX_SECRET}
    async with httpx.AsyncClient() as client:
        r = await client.get(request_url, timeout=20.0, params=query_strings)
        validate_response(r.status_code, r.text)
        response = r.json()
        return [MarketHoliday.parse_obj(item) for item in response]


# TODO: Text can sometime can be blank and we should probably hard-code
#   some error messages and return those
def validate_response(status_code: int, content: str):
    if status_code >= 400:
        raise IEXException(content)
