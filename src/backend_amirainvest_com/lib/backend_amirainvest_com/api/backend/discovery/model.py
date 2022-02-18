from typing import List, Optional

from pydantic import BaseModel


class GetModel(BaseModel):
    id: str
    first_name: str
    last_name: str
    username: str
    picture_url: Optional[str]
    chip_labels: Optional[List[str]]
    trading_strategies: Optional[List[str]]
    subscription_count: int

    class Config:
        orm_mode = True
