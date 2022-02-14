import datetime
from decimal import Decimal

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import SecurityPrices


class IntradayPricing(BaseModel):
    prices: list[SecurityPrices]


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

    five_day_pricing: list[SecurityPrices]
    max_eod_pricing: list[SecurityPrices]
