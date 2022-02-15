import asyncio
from typing import List, Tuple

import sqlalchemy as sa
from sqlalchemy.orm import Bundle
from sqlalchemy import and_, func, insert, update
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
from common_amirainvest_com.controllers.creator import get_creator_attributes
from common_amirainvest_com.s3.consts import AMIRA_POST_PHOTOS_S3_BUCKET
from common_amirainvest_com.schemas import schema
from common_amirainvest_com.schemas.schema import Bookmarks, Posts, PostsModel, UserSubscriptions
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.generic_utils import get_past_datetime
from common_amirainvest_com.utils.sqlalchemy_helpers import query_to_string


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
    subscriber_id: str,
    page_size: int = PAGE_SIZE,
    last_loaded_post_id: int = 0,
) -> Tuple[List[GetModel], FeedType]:
    wanted_feed_type = feed_wanted.feed_type
    wanted_feed_user_id = subscriber_id
    if wanted_feed_type == FeedType.creator and feed_wanted.creator_id is not None:
        wanted_feed_user_id = feed_wanted.creator_id

    returned_feed_type = wanted_feed_type
    # return_feed = await get_user_feed(wanted_feed_type, wanted_feed_user_id, page_size, last_loaded_post_id)
    discover_feed_raw = await get_discovery_feed(wanted_feed_user_id, page_size, last_loaded_post_id)
    # if return_feed == [] and wanted_feed_type != FeedType.creator:
    #     returned_feed_type = FeedType.discovery
    #     discover_feed = []
    #     user_feed_id_set = {user_post.id for user_post in return_feed}
    #
    #     discover_feed_raw = await get_discovery_feed(wanted_feed_user_id, page_size, last_loaded_post_id)
    #
    #     for discovery_post in discover_feed_raw:
    #         if discovery_post.id not in user_feed_id_set:
    #             discover_feed.append(discovery_post)
    #     return_feed = discover_feed
    #
    # return_feed = return_feed[:page_size]
    # return return_feed, returned_feed_type


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
    wanted_feed_user_id: str,
    page_size: int = PAGE_SIZE,
    last_loaded_post_id: int = 0,
) -> List[GetModel]:
    feed = await get_discovery_posts(
        wanted_feed_user_id=wanted_feed_user_id,
        last_loaded_post_id=last_loaded_post_id,
        page_size=page_size,
    )
    return feed


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
        query.where(Posts.created_at > get_past_datetime(hours=hours_ago)).order_by(Posts.id.desc()).limit(page_size)
    )

    if last_loaded_post_id != 0:
        query = query.where(Posts.id < last_loaded_post_id)
    return query


@Session
async def get_subscriber_posts(
    session: AsyncSession,
    subscriber_id: str,
    page_size: int = PAGE_SIZE,
    last_loaded_post_id: int = 0,
    hours_ago: int = MAX_HOURS_AGO,
) -> List[GetModel]:
    posts = []
    query = qf.subscriber_posts(
        subscriber_id=subscriber_id,
        page_size=page_size,
        last_loaded_post_id=last_loaded_post_id,
        hours_ago=hours_ago,
    )
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
    wanted_feed_user_id: str,
    page_size: int = PAGE_SIZE,
    last_loaded_post_id: int = 0,
    hours_ago: int = MAX_HOURS_AGO,
) -> List[GetModel]:
    subscriber_posts_cte = qf.subscriber_posts(
        subscriber_id=wanted_feed_user_id,
        page_size=-1,
        last_loaded_post_id=last_loaded_post_id,
        hours_ago=hours_ago,
    ).cte()
    subscriber_count_cte = qf.subscriber_count().cte()

    query = (
        select(
            schema.Posts,
            Bundle(
                "creator",
                schema.Users.id.label("id"),
                schema.Users.first_name.label("first_name"),
                schema.Users.last_name.label("last_name"),
                schema.Users.username.label("username"),
                schema.Users.picture_url.label("picture_url"),
                schema.Users.chip_labels.label("chip_labels"),
            ),
            sa.case(
                [
                    (Bookmarks.post_id != None, True),
                    (Bookmarks.post_id == None, False),
                ]
            ).label("is_bookmarked")
        )
        .join(
            subscriber_posts_cte,
            subscriber_posts_cte.c.id == Posts.id,
            isouter=True,
        )
        .join(
            schema.UserSubscriptions,
            schema.UserSubscriptions.creator_id == Posts.creator_id,
        )
        .join(
            subscriber_count_cte,
            subscriber_count_cte.c.creator_id == Posts.creator_id,
        )
        .join(
            schema.Users,
            schema.Users.id == schema.Posts.creator_id,
        )
        .join(
            schema.Bookmarks,
            and_(
                schema.Bookmarks.post_id == schema.Posts.id,
                schema.Bookmarks.user_id == wanted_feed_user_id,
                schema.Bookmarks.is_deleted != True,
            ),
        )
        .order_by(sa.sql.extract("day", schema.Posts.created_at).desc())
        .order_by(schema.Posts.platform.asc())
        .order_by(subscriber_count_cte.c.subscriber_count.desc())
    )
    if last_loaded_post_id != 0:
        query = query.where(schema.Posts.id < last_loaded_post_id)
    query = query.limit(page_size)

    data = (await session.execute(query)).scalars().all()
    posts = [GetModel.from_orm(post) for post in data]
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
