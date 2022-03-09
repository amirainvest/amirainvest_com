from pydantic import BaseModel


class SQSDataLoad(BaseModel):
    platform: str
    platform_unique_id: str
    creator_id: str
