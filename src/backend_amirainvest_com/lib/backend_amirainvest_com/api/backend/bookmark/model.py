import datetime
from typing import List

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import BookmarkModel as GetModel


class CreateModel(BaseModel):
    post_id: int
    is_deleted: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ListModel(BaseModel):
    results: List[GetModel]
