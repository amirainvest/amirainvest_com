from typing import List, Tuple

import sqlalchemy as sa
from sqlalchemy import insert, update
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import common_amirainvest_com.utils.query_fragments.posts as qf
from backend_amirainvest_com.api.backend.post_route.model import (
    CreateModel,
    FeedType,
    GetModel,
    ListInputModel,
    UpdateModel,
)
from backend_amirainvest_com.utils.s3 import S3
from common_amirainvest_com.s3.consts import AMIRA_POST_PHOTOS_S3_BUCKET
from common_amirainvest_com.schemas import schema
from common_amirainvest_com.utils.decorators import Session


PAGE_SIZE = 30
MAX_HOURS_AGO = 168  # NUMBER OF HOURS TO QUERY POSTGRES : 168H = 1W
MAX_FEED_SIZE = 200


@Session
async def get_controller(session: AsyncSession, post_id: int):
    return (await session.execute(select(schema.Posts).where(schema.Posts.id == post_id))).scalars().first()


@Session
async def update_controller(session: AsyncSession, user_id: str, update_data: UpdateModel) -> Row:
    return (
        await (
            session.execute(
                update(schema.Posts)
                .where(schema.Posts.creator_id == user_id)
                .where(schema.Posts.id == update_data.id)
                .values(**update_data.dict(exclude_none=True))
                .returning(schema.Posts)
            )
        )
    ).one()


@Session
async def create_controller(session: AsyncSession, user_id: str, create_data: CreateModel) -> Row:
    create_data_dict = create_data.dict(exclude_none=True)
    create_data_dict["creator_id"] = user_id
    # TODO add post to cache
    return (await session.execute(insert(schema.Posts).values(**create_data_dict).returning(schema.Posts))).one()


def upload_post_photo_controller(file_bytes: bytes, filename: str, user_id: str, post_id: int):
    return S3().upload_file_by_bytes(file_bytes, f"{user_id}/{post_id}/{filename}", AMIRA_POST_PHOTOS_S3_BUCKET)


async def list_controller(
    feed_info: ListInputModel,
    subscriber_id: str,
    page_size: int = PAGE_SIZE,
) -> Tuple[List[GetModel], FeedType]:
    wanted_feed_type = feed_info.feed_type

    return_feed = []
    return_feed_type = wanted_feed_type

    if wanted_feed_type == FeedType.creator:
        return_feed = await get_creator_feed(
            feed_info=feed_info,
            subscriber_id=subscriber_id,
            page_size=page_size,
        )
    elif wanted_feed_type == FeedType.subscriber:
        return_feed = await get_subscriber_feed(
            feed_info=feed_info,
            subscriber_id=subscriber_id,
            page_size=page_size,
        )

    if return_feed == []:
        return_feed = await get_discovery_feed(
            feed_info=feed_info,
            subscriber_id=subscriber_id,
            page_size=page_size,
        )
        return_feed_type = FeedType.discovery
    return return_feed, return_feed_type


@Session
async def get_subscriber_feed(
    session: AsyncSession,
    feed_info: ListInputModel,
    subscriber_id: str,
    page_size: int = PAGE_SIZE,
    hours_ago: int = MAX_HOURS_AGO,
) -> List[GetModel]:
    query = qf.subscriber_posts(
        subscriber_id=subscriber_id,
        page_size=page_size,
        subscriber_feed_last_loaded_post_id=feed_info.subscriber_feed_last_loaded_post_id,
        hours_ago=hours_ago,
    )
    data = await session.execute(query)
    posts = [GetModel.from_orm(post) for post in data]
    return posts


@Session
async def get_creator_feed(
    session: AsyncSession,
    feed_info: ListInputModel,
    subscriber_id: str,
    page_size: int = PAGE_SIZE,
    hours_ago: int = MAX_HOURS_AGO,
) -> List[GetModel]:
    query = qf.feed_select(subscriber_id=subscriber_id).where(schema.Posts.creator_id == feed_info.creator_id)
    query = qf.latest_posts(
        query,
        page_size=page_size,
        last_loaded_post_id=feed_info.creator_feed_last_loaded_post_id,
        hours_ago=hours_ago,
    )
    data = await session.execute(query)
    posts = [GetModel.from_orm(post) for post in data]
    return posts


@Session
async def get_discovery_feed(
    session: AsyncSession,
    feed_info: ListInputModel,
    subscriber_id: str,
    page_size: int = PAGE_SIZE,
    hours_ago: int = MAX_HOURS_AGO,
) -> List[GetModel]:
    subscriber_posts_cte = qf.subscriber_posts(
        subscriber_id=subscriber_id,
        page_size=-1,
        subscriber_feed_last_loaded_post_id=feed_info.subscriber_feed_last_loaded_post_id,
        hours_ago=hours_ago,
    ).cte()
    subscriber_count_cte = qf.subscriber_count().cte()

    query = (
        qf.feed_select(subscriber_id=subscriber_id)
        .outerjoin(
            subscriber_posts_cte,
            subscriber_posts_cte.c.id == schema.Posts.id,
        )
        .filter(subscriber_posts_cte.c.id.is_(None))
        .outerjoin(
            subscriber_count_cte,
            subscriber_count_cte.c.creator_id == schema.Posts.creator_id,
        )
        .order_by(sa.sql.extract("day", schema.Posts.created_at).desc())
        .order_by(schema.Posts.platform.asc())
        .order_by(subscriber_count_cte.c.subscriber_count.desc())
    )

    if feed_info.discovery_feed_last_loaded_post_id > 0:
        query = query.where(schema.Posts.id < feed_info.discovery_feed_last_loaded_post_id)
    query = query.limit(page_size)

    data = (await session.execute(query)).all()
    posts = [GetModel.from_orm(post) for post in data]
    return posts
