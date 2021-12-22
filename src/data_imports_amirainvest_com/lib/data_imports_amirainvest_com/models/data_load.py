from pydantic import BaseModel


class DataLoad(BaseModel):
    platform: str
    unique_platform_id: str
    creator_id: str
