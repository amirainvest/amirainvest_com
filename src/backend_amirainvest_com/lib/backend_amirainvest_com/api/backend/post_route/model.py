import enum
from typing import List, Optional

from pydantic import BaseModel, root_validator

from common_amirainvest_com.schemas.schema import MediaPlatform, PostsModel, PostsModel as GetModel


assert GetModel


class CreateModel(BaseModel):
    platform: MediaPlatform
    platform_user_id: Optional[str]
    platform_post_id: Optional[str]
    profile_img_url: Optional[str]
    text: Optional[str]
    html: Optional[str]
    title: Optional[str]
    chip_labels: Optional[List[str]]
    profile_url: Optional[str]


class UpdateModel(CreateModel):
    id: int
    platform: Optional[MediaPlatform]  # type: ignore


class FeedType(str, enum.Enum):
    subscriber = "subscriber"
    creator = "creator"
    discovery = "discovery"


class ListInputModel(BaseModel):
    feed_type: FeedType
    creator_id: Optional[str]

    @root_validator(pre=False)
    def validate_creator_id_exists_for_feed_type(cls, values):
        _feed_type = values["feed_type"]
        _creator_id = values.get("creator_id", None)

        if _feed_type == FeedType.creator and _creator_id is None:
            raise ValueError("Creator feed type requires creator_id")
        return values


class ListReturnModel(BaseModel):
    posts: List[PostsModel]
    feed_type: FeedType

    class Config:
        orm = True
        use_enum_values = True
