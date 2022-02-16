import typing as t
import datetime
from enum import Enum

from pydantic import BaseModel

from backend_amirainvest_com.utils.model import ErrorMessageModelBase, ListModelBase, StatusDetailModel
from common_amirainvest_com.schemas.schema import UsersModel as GetReturnModel


assert GetReturnModel


class SearchableAttributes(Enum):
    first_name = "first_name"
    last_name = "last_name"
    full_name = "full_name"
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
    filters: t.List[Filters] = []
    sort: t.Optional[SortModel]
    limit: int = 50


class ListReturnModel(ListModelBase[GetReturnModel]):
    pass


class UserUpdate(BaseModel):
    email: str
    username: str

    sub: t.Optional[str]

    first_name: str
    last_name: str

    bio: t.Optional[str]
    benchmark: t.Optional[int]
    chip_labels: t.Optional[list[str]]
    deleted_at: t.Optional[datetime.datetime]
    interests_diversification_rating: t.Optional[int]
    linkedin_profile: t.Optional[str]
    personal_site_url: t.Optional[str]
    picture_url: t.Optional[str]
    public_holdings_activate: t.Optional[bool]
    public_performance_activate: t.Optional[bool]
    public_profile_deactivate: t.Optional[bool]
    public_trades_activate: t.Optional[bool]
    trading_strategies: t.Optional[list[str]]

    created_at: t.Optional[datetime.datetime]
    email_verified: t.Optional[bool]
    is_claimed: t.Optional[bool]
    is_deactivated: t.Optional[bool]
    is_deleted: t.Optional[bool]


class InitReturnModel(BaseModel):
    id: str


class InitPostModel(BaseModel):
    first_name: str
    last_name: str
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
