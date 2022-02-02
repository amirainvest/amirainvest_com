import datetime
import uuid
from typing import List, Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import WatchlistFollowsModel as GetModel


assert GetModel


class CreateModel(BaseModel):
    follower_id: uuid.UUID
    watchlist_id: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class FollowedWatchlistModel(BaseModel):
    creator_id: uuid.UUID
    id: int
    name: str
    note: Optional[str]
    tickers: Optional[List[str]]
    created_at: datetime.datetime
    updated_at: datetime.datetime


class DeleteModel(BaseModel):
    id: int
