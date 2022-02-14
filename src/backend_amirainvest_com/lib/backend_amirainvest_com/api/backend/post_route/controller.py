import asyncio
from typing import List, Tuple

from sqlalchemy import func, insert, update
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.backend.post_route.model import (
    CreateModel,
    FeedType,
    GetModel,
    ListInputModel,
    UpdateModel,
)
from backend_amirainvest_com.utils.s3 import S3
from common_amirainvest_com.controllers.creator import get_creator_attributes
from common_amirainvest_com.s3.consts import AMIRA_POST_PHOTOS_S3_BUCKET
from common_amirainvest_com.schemas.schema import Bookmarks, Posts, PostsModel, UserSubscriptions
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.generic_utils import get_past_datetime


PAGE_SIZE = 30
MAX_HOURS_AGO = 168  # NUMBER OF HOURS TO QUERY POSTGRES : 168H = 1W
MAX_FEED_SIZE = 200

# TODO
#   change the feed logic to just get all posts with max feed size as limit
#   The feed should be filtering on post.id < last_loaded_post_id not >. You want to get the older posts, not newer.


@Session
async def get_controller(session: AsyncSession, post_id: int):
    return (await session.execute(select(Posts).where(Posts.id == post_id))).scalars().first()


@Session
async def update_controller(session: AsyncSession, user_id: str, update_data: UpdateModel) -> Row:
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
async def create_controller(session: AsyncSession, user_id: str, create_data: CreateModel) -> Row:
    create_data_dict = create_data.dict(exclude_none=True)
    create_data_dict["creator_id"] = user_id
    # TODO add post to cache
    return (await session.execute(insert(Posts).values(**create_data_dict).returning(Posts))).one()


async def list_controller(
    feed_wanted: ListInputModel,
    subscriber_id,
    page_size: int = PAGE_SIZE,
    last_loaded_post_id: int = 0,
) -> Tuple[List[GetModel], FeedType]:
    wanted_feed_type = feed_wanted.feed_type
    wanted_feed_user_id = subscriber_id
    if wanted_feed_type == FeedType.creator and feed_wanted.creator_id is not None:
        wanted_feed_user_id = feed_wanted.creator_id

    returned_feed_type = wanted_feed_type
    return_feed = await get_user_feed(wanted_feed_type, wanted_feed_user_id, page_size, last_loaded_post_id)

    if return_feed == [] and wanted_feed_type != FeedType.creator:
        returned_feed_type = FeedType.discovery
        discover_feed = []
        user_feed_id_set = {user_post.id for user_post in return_feed}

        discover_feed_raw = await get_discovery_feed(page_size, last_loaded_post_id)

        for discovery_post in discover_feed_raw:
            if discovery_post.id not in user_feed_id_set:
                discover_feed.append(discovery_post)
        return_feed = discover_feed

    return_feed = return_feed[:page_size]
    return return_feed, returned_feed_type


def upload_post_photo_controller(file_bytes: bytes, filename: str, user_id: str, post_id: int):
    return S3().upload_file_by_bytes(file_bytes, f"{user_id}/{post_id}/{filename}", AMIRA_POST_PHOTOS_S3_BUCKET)


async def get_user_feed(
    feed_type: FeedType,
    user_id: str,
    page_size: int = PAGE_SIZE,
    last_loaded_post_id: int = 0,
) -> List[GetModel]:
    if feed_type == FeedType.creator:
        feed = await get_creator_posts(user_id, hours_ago=MAX_HOURS_AGO)
    else:
        feed = await get_subscriber_posts(
            subscriber_id=user_id,
            page_size=page_size,
            last_loaded_post_id=last_loaded_post_id,
            hours_ago=MAX_HOURS_AGO,
        )
    pydantic_feed = orm_post_to_pydantic_post(feed)
    return pydantic_feed


async def get_discovery_feed(
    page_size: int = PAGE_SIZE,
    last_loaded_post_id: int = 0,
) -> List[GetModel]:
    feed = await get_discovery_posts(last_loaded_post_id=last_loaded_post_id, page_size=page_size)
    pydantic_feed = orm_post_to_pydantic_post(feed)
    return pydantic_feed


def orm_post_to_pydantic_post(feed: List[Posts]) -> List[GetModel]:
    end_feed = []
    for post in feed:
        end_feed.append(GetModel.parse_obj(post.dict()))
    return end_feed


def latest_posts(
    query,
    page_size: int = PAGE_SIZE,
    last_loaded_post_id: int = 0,
    hours_ago: int = MAX_HOURS_AGO,
):
    query = (
        query.where(Posts.created_at > get_past_datetime(hours=hours_ago))
        .where(Posts.id > last_loaded_post_id)
        .order_by(Posts.id.desc())
        .limit(page_size)
    )
    return query


@Session
async def get_subscriber_posts(
    session,
    subscriber_id: str,
    page_size: int = PAGE_SIZE,
    last_loaded_post_id: int = 0,
    hours_ago: int = MAX_HOURS_AGO,
) -> List[GetModel]:
    posts = []
    query = (
        select(Posts)
        .join(UserSubscriptions, UserSubscriptions.creator_id == Posts.creator_id)
        .where(UserSubscriptions.subscriber_id == subscriber_id)
    )
    query = latest_posts(query, page_size=page_size, last_loaded_post_id=last_loaded_post_id, hours_ago=hours_ago)
    data = await session.execute(query)
    for post in data.scalars().all():
        post_attributes = await get_post_attributes(post)
        posts.append(GetModel(**{**post_attributes, **post.dict()}))
    return posts


@Session
async def get_creator_posts(
    session: AsyncSession,
    creator_id: str,
    page_size: int = PAGE_SIZE,
    last_loaded_post_id: int = 0,
    hours_ago: int = MAX_HOURS_AGO,
) -> List[GetModel]:
    posts = []
    query = select(Posts).where(Posts.creator_id == creator_id)
    query = latest_posts(query, page_size=page_size, last_loaded_post_id=last_loaded_post_id, hours_ago=hours_ago)
    data = await session.execute(query)
    for post in data.scalars().all():
        post_attributes = await get_post_attributes(post)
        post = GetModel(**{**post_attributes, **post.dict()})
        posts.append(post)
    return posts


@Session
async def get_discovery_posts(
    session: AsyncSession,
    page_size: int = PAGE_SIZE,
    last_loaded_post_id: int = 0,
    hours_ago: int = MAX_HOURS_AGO,
) -> List[GetModel]:
    posts = []
    query = select(Posts).where(
        Posts.creator_id.in_(
            select(UserSubscriptions.creator_id)
            .group_by(UserSubscriptions.creator_id)
            .order_by(func.count(UserSubscriptions.creator_id))
            .limit(10)
        )
    )
    query = latest_posts(query, last_loaded_post_id, hours_ago, page_size)
    data = await session.execute(query)
    for post in data.scalars().all():
        post_attributes = await get_post_attributes(post)
        posts.append(GetModel(**{**post_attributes, **post.dict()}))
    return posts


@Session
async def get_is_bookmarked(session: AsyncSession, post_id: int):
    if (
        await session.execute(
            select(Bookmarks).where(Bookmarks.post_id == post_id).where(Bookmarks.is_deleted is not True)
        )
    ).one_or_none():
        return True
    return False


async def get_post_attributes(post: PostsModel):
    creator, is_bookmarked = await asyncio.gather(get_creator_attributes(post.creator_id), get_is_bookmarked(post.id))
    return {"creator": creator, "is_bookmarked": is_bookmarked}
