import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from common_amirainvest_com.models.creator import CreatorModel


class WatchlistItemsReturnModel(BaseModel):
    id: int
    close_price: Decimal
    current_price: Decimal
    ticker: str
    note: Optional[str]
    percent_change: Decimal


class GetModel(BaseModel):
    id: int
    name: str
    creator: CreatorModel
    items: Optional[List[WatchlistItemsReturnModel]]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class WatchlistAttributesModel(BaseModel):
    id: int
    name: str
    num_items: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class ListModel(BaseModel):
    creator: CreatorModel
    watchlists: List[WatchlistAttributesModel]


class CreateModel(BaseModel):
    name: str


class UpdateModel(BaseModel):
    id: int
    name: Optional[str]


class DeleteModel(BaseModel):
    id: int
