from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from backend_amirainvest_com.utils.model import ErrorMessageModelBase, StatusDetailModel



class ListModel(BaseModel):
    user_id: str 

    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    benchmark: Optional[str]
    chip_labels: Optional[List[str]]


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    benchmark: Optional[int]
    bio: Optional[str]
    chip_labels: Optional[List[str]]
    interests_diversification_rating: Optional[int]
    linkedin_profile: Optional[str]
    personal_site_url: Optional[str]
    picture_url: Optional[str]
    public_holdings: Optional[bool]
    public_performance: Optional[bool]
    public_profile: Optional[bool]
    public_trades: Optional[bool]

    interests_value: Optional[bool]
    interests_growth: Optional[bool]
    interests_long_term: Optional[bool]
    interests_short_term: Optional[bool]

    is_deactivated: Optional[bool]
    is_deleted: Optional[bool]


class InitReturnModel(BaseModel):
    id: str


class InitPostModel(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    benchmark: Optional[int]


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
