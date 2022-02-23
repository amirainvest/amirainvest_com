import typing as t
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from backend_amirainvest_com.api.backend.feed_route.model import GetResponseModel
from backend_amirainvest_com.utils.model import ListModelBase
from common_amirainvest_com.schemas.schema import MediaPlatform, SubscriptionLevel


assert GetResponseModel


class GetInputModel(BaseModel):
    ids: t.List[int]


class SearchableAttributes(Enum):
    content = "content"


class FilterTypes(Enum):
    substring_match = "substring_match"


class Filters(BaseModel):
    attribute: SearchableAttributes
    filter_type: FilterTypes
    value: str


class SortOrders(Enum):
    asc = "asc"
    desc = "desc"


class SortModel(BaseModel):
    attribute: SearchableAttributes
    order: SortOrders


class ListInputModel(BaseModel):
    filters: t.List[Filters] = []
    sort: t.Optional[SortModel]
    limit: int = 50


class ListReturnModel(ListModelBase[GetResponseModel]):
    pass


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
