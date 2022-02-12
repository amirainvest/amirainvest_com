import datetime
from typing import List, Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import WatchlistsModel as GetModel


assert GetModel


class CreateModel(BaseModel):
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


# class Http409Enum(Enum):
#     creator_user_missmatch = StatusDetailModel(
#         sub_status_code = 0, message="Can not create a watchlist for another user"
#     )

# class Http409Model(ErrorMessageModelBase[Http409Enum]):
#     pass
