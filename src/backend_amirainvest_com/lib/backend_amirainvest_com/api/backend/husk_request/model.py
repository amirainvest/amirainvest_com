import datetime
from typing import Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import HuskRequestsModel as GetModel, MediaPlatform


assert GetModel


class CreateModel(BaseModel):
    provided_name: str
    platform: MediaPlatform
    platform_id: str
    created_at: Optional[datetime.datetime]
    fulfilled: Optional[bool]
