import typing as t
from typing import List, Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import MediaPlatform, SubscriptionLevel


class GetInputModel(BaseModel):
    ids: t.List[int]


class CreateModel(BaseModel):
    subscription_level: SubscriptionLevel = SubscriptionLevel.standard

    title: Optional[str]
    content: str
    photos: Optional[List[str]]

    platform: MediaPlatform
    platform_display_name: Optional[str]
    platform_user_id: Optional[str]
    platform_img_url: Optional[str]
    platform_profile_url: Optional[str]
    twitter_handle: Optional[str]

    platform_post_id: Optional[str]
    platform_post_url: Optional[str]


class UpdateModel(CreateModel):
    id: int
    platform: Optional[MediaPlatform]  # type: ignore


class UploadPhotosModel(BaseModel):
    photos: List[str]
