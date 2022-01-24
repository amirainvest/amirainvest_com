import json
import uuid
from typing import List

import redis  # noqa: F401
from sqlalchemy import func, insert, update
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.backend.post_route.model import CreateModel, FeedType, ListInputModel, UpdateModel
from backend_amirainvest_com.utils.s3 import S3
from common_amirainvest_com.s3.consts import AMIRA_POST_PHOTOS_S3_BUCKET
from common_amirainvest_com.schemas.schema import Posts, UserSubscriptions
from common_amirainvest_com.utils.consts import WEBCACHE
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.generic_utils import get_class_attrs, get_past_datetime


PAGE_SIZE = 30
MAX_HOURS_AGO = 168  # NUMBER OF HOURS TO PERSIST REDIS / QUERY POSTGRES : 168H = 1W
MAX_FEED_SIZE = 200


@Session
async def get_controller(session: AsyncSession, post_id: int):
    return (await session.execute(select(Posts).where(Posts.id == post_id))).scalars().first()


@Session
async def update_controller(session: AsyncSession, user_id: uuid.UUID, update_data: UpdateModel) -> Row:
    return (
        await (
            session.execute(
                update(Posts)
                    .where(Posts.creator_id == user_id)
                    .where(Posts.id == update_data.id)
                    .values(**update_data.dict(exclude_none=True))
                    .returning(Posts)
            )
        )
    ).one()


@Session
async def create_controller(session: AsyncSession, user_id: uuid.UUID, create_data: CreateModel) -> Row:
    create_data_dict = create_data.dict(exclude_none=True)
    create_data_dict["creator_id"] = user_id
    return (await session.execute(insert(Posts).values(**create_data_dict).returning(Posts))).one()


async def list_controller(feed_wanted: ListInputModel, subscriber_id):
    feed_type = feed_wanted.feed_type
    if feed_type == FeedType.subscriber:
        posts, feed_type = await get_subscriber_feed(subscriber_id)
    elif feed_type == FeedType.creator:
        posts, feed_type = await get_creator_feed(feed_wanted.creator_id)
    elif feed_type == FeedType.discovery:
        posts, feed_type = await get_discovery_feed(subscriber_id)
    else:
        raise ValueError("feed_type invalid")

    return {"posts": [x.__dict__ for x in posts], "feed_type": feed_type}


# @router.get("/subscriber", status_code=200, response_model=Feed)
# async def get_subscriber_feed(
#     subscriber_id,
#     page: int = 0,
# ):
#     posts, feed_type = await feed.get_subscriber_feed(subscriber_id, page)
#     return {"posts": [x.__dict__ for x in posts], "feed_type": feed_type}
#
#
# @router.get("/creator", status_code=200, response_model=Feed)
# async def get_creator_feed(
#     creator_id,
#     page: int = 0,
# ):
#     posts, feed_type = await feed.get_creator_feed(creator_id, page)
#     return {"posts": [x for x in posts], "feed_type": feed_type}
#
#
# @router.get("/discovery", status_code=200, response_model=Feed)
# async def get_discovery_feed(
#     user_id: str,
#     page: int = 0,
# ):
#     posts = await feed.get_discovery_feed(user_id, page)
#     return {"posts": [x.__dict__ for x in posts], "feed_type": "discovery"}


def upload_post_photo_controller(file_bytes: bytes, filename: str, user_id: str, post_id: int):
    return S3().upload_file_by_bytes(file_bytes, f"{user_id}/{post_id}/{filename}", AMIRA_POST_PHOTOS_S3_BUCKET)


async def get_subscriber_feed(subscriber_id: str, page: int = 0, page_size: int = PAGE_SIZE) -> tuple[list[dict], str]:
    feed_type = "subscriber"
    feed = get_redis_feed(subscriber_id, feed_type, page, page_size)
    if not feed:
        feed = await get_subscriber_posts(subscriber_id, hours_ago=MAX_HOURS_AGO)
        if feed:
            update_redis_feed(subscriber_id, configure_feed(feed), feed_type)
    if not feed:
        feed_type = "discovery"
        feed = await get_discovery_feed(subscriber_id, page, page_size)
    return feed[page * page_size: (page * page_size) + page_size], feed_type


async def get_creator_feed(creator_id: str, page: int = 0, page_size: int = PAGE_SIZE) -> tuple[list[dict], str]:
    feed_type = "creator"
    feed = get_redis_feed(creator_id, feed_type, page, page_size)
    if not feed:
        feed = await get_creator_posts(creator_id, hours_ago=MAX_HOURS_AGO)
        if feed:
            update_redis_feed(creator_id, configure_feed(feed), feed_type)
    if not feed:
        feed_type = "discovery"
        feed = await get_discovery_feed(creator_id, page, page_size)
    return feed[page * page_size: (page * page_size) + page_size], feed_type


async def get_discovery_feed(user_id: str, page: int = 0, page_size: int = PAGE_SIZE):
    feed_type = "discovery"
    feed = get_redis_feed("", feed_type, page, page_size)
    if not feed:
        feed = await get_discovery_posts(hours_ago=MAX_HOURS_AGO, limit=MAX_FEED_SIZE * 5)
        if feed:
            update_redis_feed("discovery", configure_feed(feed), feed_type)
    return [x for x in feed if x.id not in [x.id for x in get_redis_feed(user_id, "subscriber")]]


def get_redis_feed(user_id: str, feed_type: str, page: int = 0, page_size: int = 30) -> List:
    key = f"{user_id}-{feed_type}"
    redis_feed = [
        json.loads(x.decode("utf-8")) for x in WEBCACHE.lrange(key, page * page_size, (page * page_size) + page_size)
    ]
    if page and page_size and redis_feed:
        redis_feed = redis_feed[page * page_size: (page * page_size) + page_size]
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


@Session
async def get_subscriber_posts(session, subscriber_id: str, hours_ago: int = 168, limit=200):
    data = await session.execute(
        select(Posts)
            .filter(
            Posts.creator_id.in_(
                select(UserSubscriptions.creator_id).where(UserSubscriptions.subscriber_id == subscriber_id)
            )
        )
            .where(Posts.created_at > get_past_datetime(hours=hours_ago))
            .order_by(Posts.created_at.desc())
            .limit(limit)
    )
    return data.scalars().all()


@Session
async def get_creator_posts(session, creator_id: str, hours_ago: int = 168, limit=200):
    data = await session.execute(
        select(Posts)
            .where(Posts.creator_id == creator_id)
            .where(Posts.created_at > get_past_datetime(hours=hours_ago))
            .order_by(Posts.created_at.desc())
            .limit(limit)
    )
    return data.scalars().all()


@Session
async def get_discovery_posts(session, hours_ago, limit=200):
    data = await session.execute(
        select(Posts)
            .where(
            Posts.creator_id.in_(
                select(UserSubscriptions.creator_id)
                    .group_by(UserSubscriptions.creator_id)
                    .order_by(func.count(UserSubscriptions.creator_id))
                    .limit(10)
            )
        )
            .where(Posts.created_at > get_past_datetime(hours=hours_ago))
            .order_by(Posts.created_at.desc())
            .limit(limit)
    )
    return data.scalars().all()
