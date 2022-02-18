from typing import List, Optional

from pydantic import BaseModel


class CreatorModel(BaseModel):
    id: str
    first_name: str
    last_name: str
    username: str
    picture_url: Optional[str]
    chip_labels: Optional[List[str]]

    class Config:
        orm_mode = True


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
