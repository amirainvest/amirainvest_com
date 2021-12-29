from hypothesis import given, strategies as st
from pydantic import BaseModel

from backend_amirainvest_com.models.feed import Feed
from common_amirainvest_com.utils.consts import WEBCACHE


@given(st.builds(Feed))
async def posts_redis_factory(posts_model: BaseModel, user_id: str, feed_type: str):
    key = f"{user_id}-{feed_type}"
    post_json = posts_model.json()
    WEBCACHE.lpush(key, post_json)
