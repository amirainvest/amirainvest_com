from typing import List, Optional

from pydantic import BaseModel


class PostCreatorModel(BaseModel):
    id_creator: str
    first_name: str
    last_name: str
    username: str
    picture_url: Optional[str]
    chip_labels: Optional[List[str]]

    class Config:
        orm_mode = True


class CreatorModel(BaseModel):
    id: Optional[str]
    first_name: str
    last_name: str
    username: str
    picture_url: Optional[str]
    chip_labels: Optional[List[str]]

    class Config:
        orm_mode = True
