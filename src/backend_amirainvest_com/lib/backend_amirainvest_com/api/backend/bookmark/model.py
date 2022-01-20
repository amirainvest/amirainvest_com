import datetime

from pydantic import BaseModel

from backend_amirainvest_com.utils.model import ListModelBase
from common_amirainvest_com.schemas.schema import BookmarkModel as GetModel


class CreateModel(BaseModel):
    post_id: int
    is_deleted: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ListModel(ListModelBase[GetModel]):
    pass
