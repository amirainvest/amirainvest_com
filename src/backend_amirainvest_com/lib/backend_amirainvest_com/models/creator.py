from pydantic import BaseModel
from typing import Optional


class Creator(BaseModel):
    id: str
    first_name: str
    last_name: str
    username: str
    picture_url: Optional[str]
