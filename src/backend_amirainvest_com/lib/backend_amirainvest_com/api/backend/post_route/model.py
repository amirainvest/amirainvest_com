from typing import List, Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import PostsModel as GetModel


assert GetModel


class CreateModel(BaseModel):
    platform: str
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
    platform: Optional[str]  # type: ignore
