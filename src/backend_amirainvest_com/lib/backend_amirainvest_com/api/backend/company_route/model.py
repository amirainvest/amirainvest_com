import datetime
import decimal
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class CompanyInfoRequest(BaseModel):
    ticker_symbol: str


class IntradayRequest(BaseModel):
    ticker_symbol: str


class FiveDayRequest(BaseModel):
    ticker_symbol: str


class SecurityPrice(BaseModel):
    price: decimal.Decimal
    price_time: datetime.datetime


class IntradayPricing(BaseModel):
    prices: list[SecurityPrice]

    class Config:
        arbitrary_types_allowed = True


class FiveDayPricing(BaseModel):
    prices: list[SecurityPrice]

    class Config:
        arbitrary_types_allowed = True


class CompanyResponse(BaseModel):
    name: str
    ticker: str
    industry: str
    ceo: str
    asset_type: str
    founding_date: datetime.date
    description: str

    week_high_52: Decimal
    week_low_52: Decimal
    open: Decimal
    close: Decimal
    market_cap: Decimal
    average_volume: Decimal

    # max_eod_pricing: list[SecurityPrices]

    class Config:
        arbitrary_types_allowed = True


class ListedCompany(BaseModel):
    name: Optional[str]
    ticker_symbol: str
