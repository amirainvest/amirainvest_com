import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class Holding(BaseModel):
    ticker: str
    ticker_price: Decimal
    ticker_price_time: datetime
    # market value / portfolio value
    percentage_of_portfolio: Decimal
    # Use this to calculate holding period
    buy_date: datetime
    # Market value of the position num shares * market price
    market_value: Decimal


class PortfolioValue(BaseModel):
    user_id: uuid.UUID
    value: Decimal
