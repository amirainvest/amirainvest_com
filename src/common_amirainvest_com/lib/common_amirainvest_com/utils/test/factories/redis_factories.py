# from hypothesis import given, strategies as st

from common_amirainvest_com.schemas.schema import PostsModel
from common_amirainvest_com.utils.consts import WEBCACHE


# TODO figure out how to generate all non None data.
# @given(st.builds(PostsModel))
def posts_redis_factory(user_id: str, feed_type: str, posts_model: PostsModel):
    key = f"{user_id}-{feed_type}"
    post_json = posts_model.json()
    WEBCACHE.lpush(key, post_json)
