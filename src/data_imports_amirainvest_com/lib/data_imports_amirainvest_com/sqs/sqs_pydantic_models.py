from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import PostsModel


class SQSDataLoad(BaseModel):
    platform: str
    unique_platform_id: str


class SQSRedisPost(BaseModel):
    user_id: str
    feed_type: str
    post: PostsModel
