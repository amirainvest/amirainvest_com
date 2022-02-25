from typing import List

from pydantic import BaseModel

from common_amirainvest_com.models.creator import CreatorModel


class ProfileModel(BaseModel):
    creator: CreatorModel
    subscription_count: int

    class Config:
        orm_mode = True


class GetModel(BaseModel):
    trading_strategy: str
    values: List[ProfileModel]

    class Config:
        orm_mode = True
