from typing import List, Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import TwitterUsers, YouTubers, SubstackUsers, ClaimablePlatform


class PlatformModel(BaseModel):
    platform: ClaimablePlatform
    username: str


class CreatePlatformModel(PlatformModel):
    is_claimed: bool = True

