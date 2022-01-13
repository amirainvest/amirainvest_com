from typing import List
from pydantic import BaseModel


class UserSearch(BaseModel):
    name: str
    user_id: str
    benchmark: str
    chip_labels: List[str]


class ContentSearch(BaseModel):
    text: str
    post_id: int
