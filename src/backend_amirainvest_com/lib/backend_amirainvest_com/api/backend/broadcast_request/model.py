from common_amirainvest_com.schemas.schema import BroadcastRequestsModel as GetModel


assert GetModel
from typing import List

from pydantic import BaseModel


class ListModel(BaseModel):
    results: List[GetModel]
