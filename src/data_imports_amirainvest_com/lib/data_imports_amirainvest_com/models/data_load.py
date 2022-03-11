from pydantic import BaseModel


class DataLoad(BaseModel):
    platform: str
    platform_unique_id: str
    creator_id: str
