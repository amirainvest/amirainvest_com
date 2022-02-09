from pydantic import BaseModel
from decimal import Decimal

class CompanyResponse(BaseModel):
    name: str
    ticker: str
    industry: str
    asset_type: str
    founding_date: str
    description: str

    week_high_52: Decimal
    week_low_52: Decimal
    open: Decimal
    close: Decimal
    market_cap: Decimal
    average_volume: Decimal
