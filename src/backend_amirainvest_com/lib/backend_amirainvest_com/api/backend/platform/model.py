from typing import List, Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import TwitterUsers, YouTubers, SubstackUsers, MediaPlatform


class PlatformModel(BaseModel):
    platform: str
    username: str


class CreatePlatformModel(PlatformModel):
    unclaimed_user: bool = False

