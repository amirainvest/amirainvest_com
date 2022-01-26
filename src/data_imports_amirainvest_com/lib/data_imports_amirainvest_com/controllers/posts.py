import json

from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import Posts, UserSubscriptions
from common_amirainvest_com.utils.consts import MAX_FEED_SIZE, WEBCACHE
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_post(session, post_data: dict):
    post = Posts(**post_data)
    session.add(post)
    return post


@Session
async def get_posts_for_subscriber(session, subscriber_id):
    data = await session.execute(
        select(Posts).where(
            Posts.creator_id.in_(
                select(UserSubscriptions.creator_id).where(UserSubscriptions.subscriber_id == subscriber_id)
            )
        )
    )
    return data.scalars().all()


async def get_posts_for_creator(session, creator_id):
    data = await session.execute(select(Posts).where(Posts.creator_id == creator_id))
    return data.scalars().all()


@Session
async def get_subscribers_for_creator(session, creator_id: str):
    data = await session.execute(select(UserSubscriptions).where(UserSubscriptions.creator_id == creator_id))
    return [x.subscriber_id for x in data.scalars().all()]


@Session
async def get_premium_subscribers_for_creator(session, creator_id: str):
    data = await session.execute(
        select(UserSubscriptions)
        .where(UserSubscriptions.creator_id == creator_id)
        .where(UserSubscriptions.subscription_level == "premium")
    )
    return [x.subscriber_id for x in data.scalars().all()]


async def put_post_on_subscriber_redis_feeds(post_data: dict, subscription_type: str = "standard"):
    subscriber_ids = []
    if subscription_type == "standard":
        subscriber_ids = await get_subscribers_for_creator(post_data["creator_id"])
    elif subscription_type == "premium":
        subscriber_ids = await get_premium_subscribers_for_creator(post_data["creator_id"])
    for subscriber_id in subscriber_ids:
        add_post_to_redis_feed(subscriber_id, {k: str(v) for k, v in post_data.items()}, feed_type="subscriber")


def put_post_on_creators_redis_feeds(post_data: dict):
    add_post_to_redis_feed(post_data["creator_id"], {k: str(v) for k, v in post_data.items()}, feed_type="creator")


def add_post_to_redis_feed(user_id: str, post: dict, feed_type: str, max_feed_size: int = MAX_FEED_SIZE):
    key = f"{user_id}-{feed_type}"
    WEBCACHE.lpush(key, json.dumps(post))
    WEBCACHE.ltrim(key, 0, max_feed_size)
