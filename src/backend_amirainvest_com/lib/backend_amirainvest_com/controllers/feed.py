import json
from typing import List

import redis  # noqa: F401

from backend_amirainvest_com.controllers import posts
from common_amirainvest_com.config import WEBCACHE
from common_amirainvest_com.schemas.schema import Posts
from common_amirainvest_com.utils.generic_utils import get_class_attrs


PAGE_SIZE = 30
MAX_HOURS_AGO = 168  # NUMBER OF HOURS TO PERSIST REDIS / QUERY POSTGRES : 168H = 1W
MAX_FEED_SIZE = 200


async def get_subscriber_feed(subscriber_id: str, page: int = 0, page_size: int = PAGE_SIZE) -> tuple[list[dict], str]:
    feed_type = "subscriber"
    feed = get_redis_feed(subscriber_id, feed_type, page, page_size)
    if not feed:
        feed = await posts.get_subscriber_posts(subscriber_id, hours_ago=MAX_HOURS_AGO)
        if feed:
            update_redis_feed(subscriber_id, configure_feed(feed), feed_type)
    if not feed:
        feed_type = "discovery"
        feed = await get_discovery_feed(subscriber_id, page, page_size)
    return feed, feed_type


async def get_creator_feed(creator_id: str, page: int = 0, page_size: int = PAGE_SIZE) -> tuple[list[dict], str]:
    feed_type = "creator"
    feed = get_redis_feed(creator_id, feed_type, page, page_size)
    if not feed:
        feed = await posts.get_creator_posts(creator_id, hours_ago=MAX_HOURS_AGO, limit=MAX_FEED_SIZE)
        if feed:
            update_redis_feed(creator_id, configure_feed(feed), feed_type)
    if not feed:
        feed_type = "discovery"
        feed = await get_discovery_feed(creator_id, page, page_size)
    return feed[page * page_size : (page * page_size) + page_size], feed_type


async def get_discovery_feed(user_id: str, page: int = 0, page_size: int = PAGE_SIZE):
    feed_type = "discovery"
    feed = get_redis_feed("", feed_type, page, page_size)
    if not feed:
        feed = await posts.get_discovery_posts(hours_ago=MAX_HOURS_AGO, limit=MAX_FEED_SIZE * 5)
        if feed:
            update_redis_feed("discovery", configure_feed(feed), feed_type)
    return [x for x in feed if x["id"] not in [x["id"] for x in get_redis_feed(user_id, "subscriber")]]


def get_redis_feed(user_id: str, feed_type: str, page: int = 0, page_size: int = 30) -> List:
    key = f"{user_id}-{feed_type}"
    redis_feed = [
        json.loads(x.decode("utf-8")) for x in WEBCACHE.lrange(key, page * page_size, (page * page_size) + page_size)
    ]
    if page and page_size and redis_feed:
        redis_feed = redis_feed[page * page_size : (page * page_size) + page_size]
    return redis_feed


def configure_feed(feed: list):
    end_feed = []
    for post in [post.__dict__ for post in feed]:
        post_dict = {}
        for k, v in post.items():
            if k in get_class_attrs(Posts):
                post_dict[k] = str(v) if k in ["creator_id", "created_at", "updated_at"] else v
            end_feed.append(post_dict)
    return end_feed


def add_post_to_redis_feed(user_id: str, post: dict, feed_type: str, max_feed_size: int = MAX_FEED_SIZE):
    key = f"{user_id}-{feed_type}"
    WEBCACHE.lpush(key, json.dumps(post))
    WEBCACHE.ltrim(key, 0, max_feed_size)


def update_redis_feed(user_id: str, feed: List[dict], feed_type: str, max_feed_size: int = MAX_FEED_SIZE):
    key = f"{user_id}-{feed_type}"
    WEBCACHE.lpush(key, *[json.dumps(post) for post in feed])
    WEBCACHE.ltrim(key, 0, max_feed_size)
