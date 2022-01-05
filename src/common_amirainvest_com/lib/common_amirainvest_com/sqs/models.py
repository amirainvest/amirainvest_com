from enum import Enum
from typing import Optional

from arrow import Arrow
from pydantic import BaseModel, validator


class MediaPlatformDataLoadQueueModel(BaseModel):
    platform: str
    unique_platform_id: str


class BrokerageDataActions(Enum):
    holdings_change = "holdings_change"
    investments_change = "investments_change"
    brokerage_change = "brokerage_change"


class Brokerage(Enum):
    plaid = "plaid"


class BrokerageDataChange(BaseModel):
    brokerage: Brokerage
    user_id: str
    token_identifier: str
    action: BrokerageDataActions
    start_date: Optional[Arrow]
    end_date: Optional[Arrow]

    @validator("start_date")
    def format_start_date(cls, value):
        return value.datetime

    @validator("end_date")
    def format_end_date(cls, value):
        return value.datetime

    class Config:
        arbitrary_types_allowed = True
