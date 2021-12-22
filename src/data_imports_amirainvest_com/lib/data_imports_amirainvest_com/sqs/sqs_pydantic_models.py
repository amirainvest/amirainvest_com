from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import Posts
from common_amirainvest_com.utils.pydantic_utils import sqlalchemy_to_pydantic


post_model = sqlalchemy_to_pydantic(Posts)


class SQSDataLoad(BaseModel):
    platform: str
    unique_platform_id: str


class SQSRedisPost(BaseModel):
    user_id: str
    feed_type: str
    post: post_model
