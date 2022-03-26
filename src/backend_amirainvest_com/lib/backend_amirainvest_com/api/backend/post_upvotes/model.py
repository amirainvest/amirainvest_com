from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import MediaPlatform

class UpvoteModel(BaseModel):
    post_id: int
    platform: MediaPlatform.InteractivePlatform()