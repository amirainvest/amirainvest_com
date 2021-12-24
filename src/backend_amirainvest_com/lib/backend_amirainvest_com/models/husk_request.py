import datetime
from typing import Optional

from pydantic import BaseModel


class CreateHuskRequestModel(BaseModel):
    twitter_user_id: Optional[str]
    youtube_channel_id: Optional[str]
    substack_username: Optional[str]
    created_at: Optional[datetime.datetime]
    fulfilled: Optional[bool]
