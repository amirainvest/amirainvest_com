from pydantic import BaseModel


class MediaPlatformDataLoadQueueModel(BaseModel):
    platform: str
    unique_platform_id: str
