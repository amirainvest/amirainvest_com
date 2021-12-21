from enum import Enum

from pydantic import BaseModel  # validator


# from arrow import Arrow
# from typing import Optional


class MediaPlatformDataLoadQueueModel(BaseModel):
    platform: str
    unique_platform_id: str


class BrokerageDataActions(Enum):
    holdings_change = "holdings_change"
    investments_change = "investments_change"


class Brokerage(Enum):
    plaid = "plaid"


# class BrokerageDataChange(BaseModel):
#     brokerage: Brokerage
#     brokerage_user_id: str
#     action: BrokerageDataActions
#     start_date: Optional[Arrow]
#     end_date: Optional[Arrow]
#
#     @validator("start_date")
#     def format_start_date(cls, value):
#         return value._datetime
#
#     @validator("end_date")
#     def format_end_date(cls, value):
#         return value._datetime
