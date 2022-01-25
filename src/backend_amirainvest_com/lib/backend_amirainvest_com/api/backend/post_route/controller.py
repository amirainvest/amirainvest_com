import uuid
from typing import List, Tuple

import redis  # noqa: F401
from sqlalchemy import func, insert, update
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.backend.post_route.model import (
    CreateModel,
    FeedType,
    ListInputModel,
    PostsModel,
    UpdateModel,
)
from backend_amirainvest_com.utils.s3 import S3
from common_amirainvest_com.s3.consts import AMIRA_POST_PHOTOS_S3_BUCKET
from common_amirainvest_com.schemas.schema import Posts, UserSubscriptions
from common_amirainvest_com.utils.consts import WEBCACHE
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.generic_utils import get_past_datetime


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


async def list_controller(
    feed_wanted: ListInputModel,
    subscriber_id,
    page: int = 0,
    page_size: int = PAGE_SIZE,
) -> Tuple[List[PostsModel], FeedType]:
    wanted_feed_type = feed_wanted.feed_type
    wanted_feed_user_id = subscriber_id if wanted_feed_type == FeedType.subscriber else feed_wanted.creator_id

    feed_start = page * page_size
    feed_end = feed_start + page_size

    returned_feed_type = wanted_feed_type
    return_feed = await get_user_feed(wanted_feed_type, wanted_feed_user_id, feed_start, feed_end)

    if return_feed == []:
        returned_feed_type = FeedType.discovery
        discover_feed = []
        user_feed_id_set = {user_post.id for user_post in return_feed}

        discover_feed_raw = await get_discovery_feed(feed_start, feed_end)

        for discovery_post in discover_feed_raw:
            if discovery_post.id not in user_feed_id_set:
                discover_feed.append(discovery_post)
        return_feed = discover_feed

    return_feed = return_feed[feed_start:feed_end]
    return return_feed, returned_feed_type


def upload_post_photo_controller(file_bytes: bytes, filename: str, user_id: str, post_id: int):
    return S3().upload_file_by_bytes(file_bytes, f"{user_id}/{post_id}/{filename}", AMIRA_POST_PHOTOS_S3_BUCKET)


async def get_user_feed(feed_type: FeedType, user_id: str, feed_start: int, feed_end: int) -> List[PostsModel]:
    pydantic_feed = get_redis_feed(user_id, feed_type, feed_start, feed_end)
    if pydantic_feed == []:
        if feed_type == FeedType.creator:
            feed = await get_creator_posts(user_id, hours_ago=MAX_HOURS_AGO)
        else:
            feed = await get_subscriber_posts(user_id, hours_ago=MAX_HOURS_AGO)
        pydantic_feed = orm_post_to_pydantic_post(feed)
        if pydantic_feed != []:
            update_redis_feed(user_id, feed_type, pydantic_feed)
    return pydantic_feed


async def get_discovery_feed(feed_start: int, feed_end: int) -> List[PostsModel]:
    pydantic_feed = get_redis_feed(FeedType.discovery.value, FeedType.discovery, feed_start, feed_end)
    if pydantic_feed == []:
        feed = await get_discovery_posts(hours_ago=MAX_HOURS_AGO, limit=MAX_FEED_SIZE * 5)
        pydantic_feed = orm_post_to_pydantic_post(feed)
        if pydantic_feed != []:
            update_redis_feed(FeedType.discovery, FeedType.discovery, pydantic_feed)
    return pydantic_feed


def get_redis_feed(user_id: str, feed_type: FeedType, feed_start: int, feed_end: int) -> List[PostsModel]:
    key = f"{user_id}-{feed_type.value}"
    redis_feed_raw = WEBCACHE.lrange(key, feed_start, feed_end)
    redis_feed = []
    for post in redis_feed_raw:
        redis_feed.append(PostsModel.parse_raw(post))
    return redis_feed


def orm_post_to_pydantic_post(feed: List[Posts]) -> List[PostsModel]:
    end_feed = []
    for post in feed:
        end_feed.append(PostsModel.parse_obj(post.dict()))
    return end_feed


def add_post_to_redis_feed(user_id: str, post: PostsModel, feed_type: str, max_feed_size: int = MAX_FEED_SIZE):
    key = f"{user_id}-{feed_type}"
    WEBCACHE.lpush(key, post.json(exclude_none=True))
    WEBCACHE.ltrim(key, 0, max_feed_size)


def update_redis_feed(user_id: str, feed_type: FeedType, feed: List[PostsModel], max_feed_size: int = MAX_FEED_SIZE):
    key = f"{user_id}-{feed_type.value}"
    WEBCACHE.lpush(key, *[post.json(exclude_none=True) for post in feed])
    WEBCACHE.ltrim(key, 0, max_feed_size)


@Session
async def get_subscriber_posts(session, subscriber_id: str, hours_ago: int = 168, limit=200) -> List[Posts]:
    data = await session.execute(
        select(Posts)
        .join(UserSubscriptions, UserSubscriptions.creator_id == Posts.creator_id)
        .where(UserSubscriptions.subscriber_id == subscriber_id)
        .where(Posts.created_at > get_past_datetime(hours=hours_ago))
        .order_by(Posts.created_at.desc())
        .limit(limit)
    )
    return data.scalars().all()


@Session
async def get_creator_posts(
    session, creator_id: str, hours_ago: int = MAX_HOURS_AGO, limit=MAX_FEED_SIZE
) -> List[Posts]:
    data = await session.execute(
        select(Posts)
        .where(Posts.creator_id == creator_id)
        .where(Posts.created_at > get_past_datetime(hours=hours_ago))
        .order_by(Posts.created_at.desc())
        .limit(limit)
    )
    return data.scalars().all()


@Session
async def get_discovery_posts(session, hours_ago, limit=MAX_FEED_SIZE * 5) -> List[Posts]:
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
