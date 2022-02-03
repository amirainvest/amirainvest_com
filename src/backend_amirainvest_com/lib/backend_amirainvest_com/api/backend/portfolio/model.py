from decimal import Decimal
from arrow import Arrow

from pydantic import BaseModel, validator


class Holding(BaseModel):
    ticker: str
    ticker_price: Decimal
    ticker_price_time: Arrow
    # market value / portfolio value
    percentage_of_portfolio: Decimal
    # Use this to calculate holding period
    buy_date: Arrow
    # Market value of the position num shares * market price
    market_value: Decimal

    @validator("ticker_price_time")
    def format_start_date(cls, value):
        if value is None:
            return None
        return value.datetime

    @validator("buy_date")
    def format_start_date(cls, value):
        if value is None:
            return None
        return value.datetime

    class Config:
        arbitrary_types_allowed = True
