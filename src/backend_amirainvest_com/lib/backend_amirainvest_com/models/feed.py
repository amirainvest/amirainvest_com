from enum import Enum

from pydantic import BaseModel
from typing import List
from common_amirainvest_com.schemas.schema import PostsModel


class FeedType(str, Enum):
    subscriber = "subscriber"
    creator = "creator"
    discovery = "discovery"


class Feed(BaseModel):
    posts: List[PostsModel]
    feed_type: FeedType

    class Config:
        orm = True
        use_enum_values = True
