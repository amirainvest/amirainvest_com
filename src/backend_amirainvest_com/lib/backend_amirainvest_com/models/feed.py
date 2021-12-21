from enum import Enum

from pydantic import BaseModel


class FeedType(str, Enum):
    subscriber = "subscriber"
    creator = "creator"
    discovery = "discovery"


class Feed(BaseModel):
    posts: list
    feed_type: FeedType

    class Config:
        orm = True
        use_enum_values = True
