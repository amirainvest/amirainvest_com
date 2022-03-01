from pydantic import BaseModel

from backend_amirainvest_com.utils.model import ListModelBase
from common_amirainvest_com.schemas.schema import BookmarkModel as GetModel


class CreateModel(BaseModel):
    post_id: int


class ListModel(ListModelBase[GetModel]):
    pass
