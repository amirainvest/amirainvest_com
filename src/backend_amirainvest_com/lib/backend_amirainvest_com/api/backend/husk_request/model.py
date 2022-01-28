import datetime
from typing import Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import HuskPlatforms, HuskRequestsModel as GetModel


assert GetModel


class CreateModel(BaseModel):
    provided_name: str
    platform: HuskPlatforms
    platform_id: str
    created_at: Optional[datetime.datetime]
    fulfilled: Optional[bool]
