import datetime
from typing import Optional

from pydantic import BaseModel
from common_amirainvest_com.schemas.schema import Platforms


class CreateHuskRequestModel(BaseModel):
    platform: Platforms
    platform_id: str
    created_at: Optional[datetime.datetime]
    fulfilled: Optional[bool]
