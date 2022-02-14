from pydantic import BaseModel


class SQSDataLoad(BaseModel):
    platform: str
    unique_platform_id: str
