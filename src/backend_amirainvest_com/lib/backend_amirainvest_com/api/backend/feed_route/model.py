import datetime
import enum
from typing import List, Optional

from pydantic import BaseModel, root_validator

from common_amirainvest_com.models.creator import Creator
from common_amirainvest_com.schemas.schema import MediaPlatform, SubscriptionLevel


class GetResponseModel(BaseModel):
    class Config:
        orm_mode = True

    id: int

    creator: Creator
    is_bookmarked: bool
    subscription_level: SubscriptionLevel = SubscriptionLevel.standard

    title: Optional[str]
    content: Optional[str]
    photos: Optional[List[str]]

    platform: MediaPlatform
    platform_display_name: Optional[str]
    platform_user_id: Optional[str]
    platform_img_url: Optional[str]
    platform_profile_url: Optional[str]
    twitter_handle: Optional[str]

    platform_post_id: Optional[str]
    platform_post_url: Optional[str]

    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class FeedType(str, enum.Enum):
    subscriber = "subscriber"
    creator = "creator"
    discovery = "discovery"


class ListInputModel(BaseModel):
    feed_type: FeedType
    creator_id: Optional[str]
    company_ticker: Optional[str]
    subscriber_feed_last_loaded_date: datetime.datetime
    creator_feed_last_loaded_date: datetime.datetime
    discovery_feed_last_loaded_date: datetime.datetime

    @root_validator(pre=False)
    def validate_creator_id_exists_for_feed_type(cls, values):
        _feed_type = values["feed_type"]
        _creator_id = values.get("creator_id", None)

        if _feed_type == FeedType.creator and _creator_id is None:
            raise ValueError("Creator feed type requires creator_id")
        return values


class ListReturnModel(BaseModel):
    posts: List[GetResponseModel]
    feed_type: FeedType

    class Config:
        orm = True
        use_enum_values = True
