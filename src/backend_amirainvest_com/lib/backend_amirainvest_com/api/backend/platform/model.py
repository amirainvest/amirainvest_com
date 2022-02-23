from typing import List, Optional
from enum import Enum

from pydantic import BaseModel

from backend_amirainvest_com.utils.model import ErrorMessageModelBase, StatusDetailModel
from common_amirainvest_com.schemas.schema import TwitterUsers, YouTubers, SubstackUsers, ClaimablePlatform


class PlatformModel(BaseModel):
    platform: ClaimablePlatform
    username: str


class CreatePlatformModel(PlatformModel):
    is_claimed: bool = True


class Http409Enum(Enum):
    platforms_match_unclaimed_husk = StatusDetailModel(
        sub_status_code=0, message="Platform usernames match unclaimed husk platforms"
    )
    platforms_match_claimed_user = StatusDetailModel(
        sub_status_code=1, 
        message="Platform usernames have been claimed by a user. Contact us if this is an error at contact@amirainvest.com"
    )

class Http409Model(ErrorMessageModelBase[Http409Enum]):
    pass