import datetime
import enum
import uuid
from decimal import Decimal
from typing import Optional

from dateutil import parser
from pydantic import BaseModel, validator


class HoldingsRequest(BaseModel):
    user_id: str


class PortfolioRequest(BaseModel):
    user_id: str
    symbols: list[str]
    last_trade_date: Optional[datetime.datetime]
    limit: int = 50

    @validator("last_trade_date", pre=True)
    def parse_last_trade_date(cls, value):
        if isinstance(value, str):
            return parser.isoparse(value).date()
        return value


class PortfolioSummaryRequest(BaseModel):
    user_id: str
    start_date: datetime.date
    end_date: datetime.date

    @validator("start_date", pre=True)
    def parse_start_date(cls, value):
        if isinstance(value, str):
            return parser.isoparse(value).date()
        return value

    @validator("end_date", pre=True)
    def parse_end_date(cls, value):
        if isinstance(value, str):
            return parser.isoparse(value).date()
        return value


class Holding(BaseModel):
    ticker: str
    ticker_price: Decimal
    ticker_price_time: datetime.datetime
    percentage_of_portfolio: Decimal
    buy_date: datetime.datetime
    return_percentage: Optional[Decimal]
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


class HoldingPeriod(BaseModel):
    date: datetime.date
    market_value: Decimal
    rate: Decimal


class PortfolioResponse(BaseModel):
    user_id: str
    return_history: Optional[list[HistoricalReturn]]
    benchmark_return_history: Optional[list[HistoricalReturn]]
    portfolio_allocation: Optional[list[Optional[SectionAllocation]]]
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
