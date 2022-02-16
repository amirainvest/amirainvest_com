from typing import List, Tuple

import sqlalchemy as sa
from sqlalchemy import Date
from sqlalchemy.ext.asyncio import AsyncSession

import common_amirainvest_com.utils.query_fragments.feed as qf
from backend_amirainvest_com.api.backend.feed_route.model import FeedType, GetResponseModel, ListInputModel
from common_amirainvest_com.schemas import schema
from common_amirainvest_com.utils.decorators import Session


async def list_controller(
    feed_info: ListInputModel,
    subscriber_id: str,
    page_size: int = qf.PAGE_SIZE,
) -> Tuple[List[GetResponseModel], FeedType]:
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
    page_size: int = qf.PAGE_SIZE,
    hours_ago: int = qf.MAX_HOURS_AGO,
) -> List[GetResponseModel]:
    query = qf.subscriber_posts(
        subscriber_id=subscriber_id,
        page_size=page_size,
        subscriber_feed_last_loaded_post_id=feed_info.subscriber_feed_last_loaded_post_id,
        hours_ago=hours_ago,
    )
    data = await session.execute(query)
    posts = [GetResponseModel.from_orm(post) for post in data]
    return posts


@Session
async def get_creator_feed(
    session: AsyncSession,
    feed_info: ListInputModel,
    subscriber_id: str,
    page_size: int = qf.PAGE_SIZE,
    hours_ago: int = qf.MAX_HOURS_AGO,
) -> List[GetResponseModel]:
    query = qf.feed_select(subscriber_id=subscriber_id).where(schema.Posts.creator_id == feed_info.creator_id)
    query = qf.latest_posts(
        query,
        page_size=page_size,
        last_loaded_post_id=feed_info.creator_feed_last_loaded_post_id,
        hours_ago=hours_ago,
    )
    data = await session.execute(query)
    posts = [GetResponseModel.from_orm(post) for post in data]
    return posts


@Session
async def get_discovery_feed(
    session: AsyncSession,
    feed_info: ListInputModel,
    subscriber_id: str,
    page_size: int = qf.PAGE_SIZE,
    hours_ago: int = qf.MAX_HOURS_AGO,
) -> List[GetResponseModel]:
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
            .order_by(sa.cast(schema.Posts.created_at, Date).desc())
            .order_by(schema.Posts.platform.asc())
            .order_by(subscriber_count_cte.c.subscriber_count.desc())
    )

    if feed_info.discovery_feed_last_loaded_post_id > 0:
        query = query.where(schema.Posts.id < feed_info.discovery_feed_last_loaded_post_id)
    query = query.limit(page_size)

    data = (await session.execute(query)).all()
    posts = [GetResponseModel.from_orm(post) for post in data]
    return posts
