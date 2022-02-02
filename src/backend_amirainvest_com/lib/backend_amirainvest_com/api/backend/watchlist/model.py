import datetime
import uuid
from typing import List, Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import WatchlistsModel as GetModel


assert GetModel


class CreateModel(BaseModel):
    creator_id: uuid.UUID
    name: str
    tickers: List[str]
    note: Optional[str]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class UpdateModel(BaseModel):
    id: int
    name: Optional[str]
    tickers: Optional[List[str]]
    note: Optional[str]


class DeleteModel(BaseModel):
    id: int