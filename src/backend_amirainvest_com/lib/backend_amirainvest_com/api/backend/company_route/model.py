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
    asset_type: Optional[str]
    founding_date: Optional[datetime.date]
    description: str

    week_high_52: Optional[Decimal]
    week_low_52: Optional[Decimal]
    open: Optional[Decimal]
    close: Optional[Decimal]
    market_cap: Optional[Decimal]
    average_volume: Optional[Decimal]

    max_eod_pricing: list[SecurityPrice]

    class Config:
        arbitrary_types_allowed = True


class ListedCompany(BaseModel):
    name: Optional[str]
    ticker_symbol: str