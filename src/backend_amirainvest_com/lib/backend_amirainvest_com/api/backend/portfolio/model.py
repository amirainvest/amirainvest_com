import datetime
import enum
import uuid
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class PortfolioRequest(BaseModel):
    user_id: str


class Holding(BaseModel):
    ticker: str
    ticker_price: Decimal
    ticker_price_time: datetime.datetime
    percentage_of_portfolio: Decimal
    buy_date: datetime.datetime
    return_percentage: Decimal
    market_value: Decimal


class PortfolioValue(BaseModel):
    user_id: uuid.UUID
    value: Decimal


class HistoricalTrade(BaseModel):
    trade_date: datetime.datetime
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


class HistoricalReturn(BaseModel):
    date: datetime.date
    daily_return: Decimal


class SectionAllocation(BaseModel):
    name: str
    percentage: Decimal


class HistoricalPeriod(BaseModel):
    date: datetime.date
    mv: Decimal
    hp: Decimal


class PortfolioResponse(BaseModel):
    user_id: str
    return_history: Optional[list[HistoricalReturn]]
    benchmark_return_history: Optional[list[HistoricalReturn]]
    portfolio_allocation: Optional[list[SectionAllocation]]
    total_return: Decimal
    beta: Decimal
    sharpe_ratio: Decimal
    percentage_long: Decimal
    percentage_short: Decimal
    percentage_gross: Decimal
    percentage_net: Decimal
    portfolio_type: PortfolioType


class MarketValue(BaseModel):
    value: Decimal
    date: datetime.date
