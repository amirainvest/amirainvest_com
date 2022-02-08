import enum
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


class HistoricalTrade(BaseModel):
    trade_date: datetime
    ticker: str
    transaction_type: str
    transaction_price: Decimal
    transaction_market_value: Decimal
    percentage_change_in_position: Decimal


class PortfolioType(enum.Enum):
    User = "user"
    Creator = "creator"


class TradingHistoryResponse(BaseModel):
    trades: list[HistoricalTrade]
    portfolio_type: PortfolioType


class HoldingsResponse(BaseModel):
    holdings: list[Holding]
    portfolio_type: PortfolioType