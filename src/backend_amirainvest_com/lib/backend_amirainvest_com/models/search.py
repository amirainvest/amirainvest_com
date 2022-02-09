from typing import List, Optional

from pydantic import BaseModel


class UserSearch(BaseModel):
    user_id: str

    first_name: Optional[str]
    last_name: Optional[str]
    benchmark: Optional[str]
    chip_labels: Optional[List[str]]


class ContentSearch(BaseModel):
    text: str
    post_id: int
