import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import WatchlistItemsModel as GetModel
from backend_amirainvest_com.utils.model import ErrorMessageModelBase, StatusDetailModel


assert GetModel



class DeleteModel(BaseModel):
    id: int


class UpdateModel(DeleteModel):
    note: Optional[str]


class CreateModel(BaseModel):
    watchlist_id: int
    ticker: str
    note: Optional[str]


class Http409Enum(Enum):
    bad_ticker = StatusDetailModel(
        sub_status_code=0, message="Ticker Not Acceptable, Not in Securities Table"
    )
    duplicate_ticker = StatusDetailModel(
        sub_status_code=1, message="Ticker Not Acceptable, Already exists in Watchlist"
    )


class Http409Model(ErrorMessageModelBase[Http409Enum]):
    pass


class Http403Enum(Enum):
    not_watchlist_owner = StatusDetailModel(
        sub_status_code=0, message="User is not the owner of the watchlist"
    )

class Http403Model(ErrorMessageModelBase[Http403Enum]):
    pass