from sqlalchemy import func
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import Posts, UserSubscriptions
from common_amirainvest_com.utils.database_utils import update
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.generic_utils import get_past_datetime


@Session
async def get_post(session, post_id: int):
    return (await session.execute(select(Posts).where(Posts.id == post_id))).scalars().first()


async def update_post(amira_post_data: dict):
    return await update(Posts, amira_post_data)


@Session
async def create_post(session, post_data: dict):
    post = Posts(**post_data)
    session.add(post)
    return post


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
