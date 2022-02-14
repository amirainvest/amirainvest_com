import decimal
import enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator


class MarketHolidayDirection(enum.Enum):
    last = "last"
    next = "next"


class MarketHoliday(BaseModel):
    date: datetime
    settlementDate: datetime

    @validator("date", pre=True)
    def parse_date(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d")
        return value

    @validator("settlementDate", pre=True)
    def parse_settlementDate(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d")
        return value


class Symbol(BaseModel):
    symbol: Optional[str]
    exchange: Optional[str]
    name: Optional[str]
    date: Optional[str]
    isEnabled: Optional[bool]
    type: Optional[str]
    region: Optional[str]
    currency: Optional[str]
    iexId: Optional[str]
    figi: Optional[str]
    cik: Optional[str]


class IEXSymbol(BaseModel):
    symbol: Optional[str]
    date: Optional[str]
    isEnabled: Optional[bool]


class Company(BaseModel):
    symbol: Optional[str]
    companyName: Optional[str]
    employees: Optional[int]
    exchange: Optional[str]
    industry: Optional[str]
    website: Optional[str]
    description: Optional[str]
    CEO: Optional[str]
    securityName: Optional[str]
    issueType: Optional[str]
    sector: Optional[str]
    primarySicCode: Optional[int]
    tags: Optional[list[str]]
    address: Optional[str]
    address2: Optional[str]
    state: Optional[str]
    city: Optional[str]
    zip: Optional[str]
    country: Optional[str]
    phone: Optional[str]


class HistoricalPriceEnum(enum.Enum):
    Max = "max"
    TwoYear = "2y"
    OneYear = "1y"
    YearToDate = "ytd"
    SixMonths = "6m"
    ThreeMonths = "3m"
    OneMonth = "1m"
    OneMonth30MinuteIntervals = "3mm"
    FiveDays = "5d"
    FiveDays10MinuteIntervals = "5dm"
    OneDay = "dynamic"  # 1d or 1m data depending on day or week and time of time


class HistoricalPrice(BaseModel):
    close: Optional[decimal.Decimal]
    high: Optional[decimal.Decimal]
    low: Optional[decimal.Decimal]
    open: Optional[decimal.Decimal]
    symbol: Optional[str]
    volume: Optional[decimal.Decimal]
    id: Optional[str]
    key: Optional[str]
    date: Optional[str]
    updated: Optional[decimal.Decimal]
    changeOverTime: Optional[decimal.Decimal]
    marketChangeOverTime: Optional[decimal.Decimal]
    uOpen: Optional[decimal.Decimal]
    uClose: Optional[decimal.Decimal]
    uHigh: Optional[decimal.Decimal]
    uLow: Optional[decimal.Decimal]
    uVolume: Optional[decimal.Decimal]
    fOpen: Optional[decimal.Decimal]
    fClose: Optional[decimal.Decimal]
    fHigh: Optional[decimal.Decimal]
    fLow: Optional[decimal.Decimal]
    fVolume: Optional[decimal.Decimal]
    label: Optional[str]
    change: Optional[decimal.Decimal]
    changePercent: Optional[decimal.Decimal]


class HistoricalPriceFiveDay(BaseModel):
    date: Optional[str]
    minute: Optional[str]
    label: Optional[str]
    open: Optional[decimal.Decimal]
    high: Optional[decimal.Decimal]
    low: Optional[decimal.Decimal]
    close: Optional[decimal.Decimal]
    average: Optional[decimal.Decimal]
    volume: Optional[decimal.Decimal]
    notional: Optional[decimal.Decimal]
    numberOfTrades: Optional[decimal.Decimal]
    marketOpen: Optional[decimal.Decimal]
    marketHigh: Optional[decimal.Decimal]
    marketLow: Optional[decimal.Decimal]
    marketClose: Optional[decimal.Decimal]
    marketAverage: Optional[decimal.Decimal]
    marketVolume: Optional[decimal.Decimal]
    marketNotational: Optional[decimal.Decimal]
    marketNumberOfTrades: Optional[decimal.Decimal]


class IntradayPrice(BaseModel):
    date: Optional[str]
    minute: Optional[str]
    label: Optional[str]
    marketOpen: Optional[decimal.Decimal]
    marketClose: Optional[decimal.Decimal]
    marketHigh: Optional[decimal.Decimal]
    marketLow: Optional[decimal.Decimal]
    marketAverage: Optional[decimal.Decimal]
    marketVolume: Optional[decimal.Decimal]
    marketNotional: Optional[decimal.Decimal]
    marketNumberOfTrades: Optional[decimal.Decimal]
    marketChangeOverTime: Optional[decimal.Decimal]
    high: Optional[decimal.Decimal]
    low: Optional[decimal.Decimal]
    open: Optional[decimal.Decimal]
    close: Optional[decimal.Decimal]
    average: Optional[decimal.Decimal]
    volume: Optional[decimal.Decimal]
    notional: Optional[decimal.Decimal]
    numberOfTrades: Optional[decimal.Decimal]
    changeOverTime: Optional[decimal.Decimal]


class StockQuote(BaseModel):
    avgTotalVolume: Optional[decimal.Decimal]
    calculationPrice: Optional[str]
    change: Optional[decimal.Decimal]
    changePercent: Optional[decimal.Decimal]
    companyName: Optional[str]
    close: Optional[decimal.Decimal]
    closeSource: Optional[str]
    closeTime: Optional[int]
    currency: Optional[str]
    delayedPrice: Optional[decimal.Decimal]
    delayedPriceTime: Optional[int]
    extendedChange: Optional[decimal.Decimal]
    extendedChangePercent: Optional[decimal.Decimal]
    extendedPrice: Optional[decimal.Decimal]
    extendedPriceTime: Optional[int]
    high: Optional[decimal.Decimal]
    highSource: Optional[str]
    highTime: Optional[int]
    iexAskPrice: Optional[decimal.Decimal]
    iexAskSize: Optional[decimal.Decimal]
    iexBidPrice: Optional[decimal.Decimal]
    iexBidSize: Optional[decimal.Decimal]
    iexClose: Optional[decimal.Decimal]
    iexCloseTime: Optional[int]
    iexLastUpdated: Optional[int]
    iexMarketPercent: Optional[decimal.Decimal]
    iexOpen: Optional[decimal.Decimal]
    iexOpenTime: Optional[int]
    iexRealtimePrice: Optional[decimal.Decimal]
    iexRealtimeSize: Optional[decimal.Decimal]
    iexVolume: Optional[decimal.Decimal]
    lastTradeTime: Optional[int]
    latestPrice: Optional[decimal.Decimal]
    latestSource: Optional[str]
    latestTime: Optional[str]
    latestUpdate: Optional[int]
    latestVolume: Optional[decimal.Decimal]
    low: Optional[decimal.Decimal]
    lowSource: Optional[str]
    lowTime: Optional[int]
    marketCap: Optional[decimal.Decimal]
    oddLotDelayedPrice: Optional[decimal.Decimal]
    oddLotDelayedPriceTime: Optional[int]
    open: Optional[decimal.Decimal]
    openTime: Optional[int]
    openSource: Optional[str]
    peRatio: Optional[decimal.Decimal]
    previousClose: Optional[decimal.Decimal]
    previousVolume: Optional[decimal.Decimal]
    primaryExchange: Optional[str]
    symbol: Optional[str]
    volume: Optional[decimal.Decimal]
    week52High: Optional[decimal.Decimal]
    week52Low: Optional[decimal.Decimal]
    ytdChange: Optional[decimal.Decimal]
    isUSMarketOpen: Optional[bool]
