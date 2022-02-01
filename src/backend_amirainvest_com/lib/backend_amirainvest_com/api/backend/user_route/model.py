import typing as t
import uuid
from enum import Enum

from pydantic import BaseModel

from backend_amirainvest_com.utils.model import ErrorMessageModelBase, StatusDetailModel


class SearchableAttributes(Enum):
    name = "name"
    username = "username"


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
    filters: t.List[Filters]
    sort: t.Optional[SortModel]
    limit: int = 50


class ListReturnModel(BaseModel):
    user_id: str

    name: t.Optional[str]
    benchmark: t.Optional[str]
    chip_labels: t.Optional[t.List[str]]


class UserUpdate(BaseModel):
    name: t.Optional[str]
    bio: t.Optional[str]
    personal_site_url: t.Optional[str]
    linkedin_profile: t.Optional[str]
    interests_value: t.Optional[bool]
    interests_growth: t.Optional[bool]
    interests_long_term: t.Optional[bool]
    interests_short_term: t.Optional[bool]
    interests_diversification_rating: t.Optional[int]
    benchmark: t.Optional[str]
    chip_labels: t.Optional[t.List[str]]
    public_profile: t.Optional[bool]
    public_performance: t.Optional[bool]
    public_holdings: t.Optional[bool]
    public_trades: t.Optional[bool]
    is_deactivated: t.Optional[bool]
    is_deleted: t.Optional[bool]


class InitReturnModel(BaseModel):
    id: uuid.UUID


class InitPostModel(BaseModel):
    name: str
    username: str
    email: str


class Http409Enum(Enum):
    user_sub_missmatch = StatusDetailModel(
        sub_status_code=0, message="User with sub exists, and does not match email passed"
    )
    app_metadata_includes_user_id = StatusDetailModel(
        sub_status_code=1, message="Token already includes app_metadata.user_id"
    )


class Http409Model(ErrorMessageModelBase[Http409Enum]):
    pass


class Http400Enum(Enum):
    auth0_app_metadata_failed = StatusDetailModel(
        sub_status_code=0, message="Failed to change auth0 app_metadata for user."
    )


class Http400Model(ErrorMessageModelBase[Http400Enum]):
    pass
