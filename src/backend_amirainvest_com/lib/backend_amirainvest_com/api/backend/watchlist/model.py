import datetime
from typing import List, Optional
from decimal import Decimal

from pydantic import BaseModel

from common_amirainvest_com.models.creator import CreatorModel
from common_amirainvest_com.schemas.schema import WatchlistsModel


class WatchlistItemsReturnModel(BaseModel):
    close_price: int
    current_price: int
    ticker: str
    note: Optional[str]
    percent_change: Decimal


class GetModel(BaseModel):
    watchlist: Optional[WatchlistsModel]
    items: Optional[List[WatchlistItemsReturnModel]]
    creator: CreatorModel


class WatchlistAttributesModel(BaseModel):
    watchlist: Optional[WatchlistsModel]
    items: Optional[List[WatchlistItemsReturnModel]]


class ListModel(BaseModel):
    creator: CreatorModel
    watchlists: List[WatchlistAttributesModel]


class CreateModel(BaseModel):
    creator_id: str
    name: str
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class UpdateModel(BaseModel):
    id: int
    name: Optional[str]
    tickers: Optional[List[str]]
    note: Optional[str]


class DeleteModel(BaseModel):
    id: int
