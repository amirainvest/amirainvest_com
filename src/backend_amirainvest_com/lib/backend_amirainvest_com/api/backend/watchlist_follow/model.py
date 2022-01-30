import datetime
import uuid
from typing import Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import WatchlistsModel as GetModel


assert GetModel


class CreateModel(BaseModel):
    id: int
    follower_id: uuid.UUID
    watchlist_id: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class DeleteModel(BaseModel):
    id: int
