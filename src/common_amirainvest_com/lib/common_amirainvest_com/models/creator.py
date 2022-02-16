from typing import List, Optional

from pydantic import BaseModel


class Creator(BaseModel):
    id_creator: str
    first_name: str
    last_name: str
    username: str
    picture_url: Optional[str]
    chip_labels: Optional[List[str]]

    class Config:
        orm_mode = True
