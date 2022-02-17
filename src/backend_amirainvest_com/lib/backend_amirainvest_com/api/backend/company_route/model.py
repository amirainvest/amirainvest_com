import datetime
import decimal
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class CompanyRequest(BaseModel):
    ticker_symbol: str


class SecurityPrice(BaseModel):
    price: decimal.Decimal
    price_time: datetime.datetime


class PricingResponse(BaseModel):
    prices: list[SecurityPrice]


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


class ListedCompany(BaseModel):
    name: Optional[str]
    ticker_symbol: str
