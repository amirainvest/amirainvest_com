import datetime
from typing import Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import WatchlistFollowsModel as GetModel


assert GetModel


class CreateModel(BaseModel):
    watchlist_id: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class WatchlistAttributesModel(BaseModel):
    id: int
    name: str
    num_items: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class DeleteModel(BaseModel):
    id: int
