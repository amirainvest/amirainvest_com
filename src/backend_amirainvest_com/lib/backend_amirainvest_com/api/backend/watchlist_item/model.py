import datetime
from typing import Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import WatchlistItemsModel as GetModel


assert GetModel


class CreateModel(BaseModel):
    watchlist_id: int
    ticker: str
    note: Optional[str]
    created_at: Optional[datetime.datetime]


class UpdateModel(BaseModel):
    id: int
    ticker: str
    note: Optional[str]


class DeleteModel(BaseModel):
    id: int
