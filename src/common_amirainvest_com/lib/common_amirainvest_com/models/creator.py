from typing import Optional, List

from pydantic import BaseModel


class Creator(BaseModel):
    id: str
    first_name: str
    last_name: str
    username: str
    picture_url: Optional[str]
    chip_labels: Optional[List[str]]
