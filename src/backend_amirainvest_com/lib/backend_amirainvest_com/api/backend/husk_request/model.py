import datetime
from typing import Optional

from pydantic import BaseModel

from backend_amirainvest_com.utils.model import ListModelBase
from common_amirainvest_com.schemas.schema import HuskRequestsModel as GetModel


assert GetModel


class CreateModel(BaseModel):
    twitter_user_id: Optional[str]
    youtube_channel_id: Optional[str]
    substack_username: Optional[str]
    created_at: Optional[datetime.datetime]
    fulfilled: Optional[bool]


class ListModel(ListModelBase[GetModel]):
    pass
