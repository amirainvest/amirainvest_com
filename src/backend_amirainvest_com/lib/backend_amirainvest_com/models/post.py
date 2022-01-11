import datetime
import uuid
from typing import List, Optional

from pydantic import BaseModel


class PostCreate(BaseModel):
    creator_id: uuid.UUID
    platform: str
    platform_user_id: Optional[str]
    platform_post_id: Optional[str]
    profile_img_url: Optional[str]
    text: Optional[str]
    html: Optional[str]
    title: Optional[str]
    chip_labels = Optional[List[str]]
    profile_url: Optional[str]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
