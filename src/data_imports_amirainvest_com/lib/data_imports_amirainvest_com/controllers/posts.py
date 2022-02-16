from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import Posts, UserSubscriptions
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_post(session, post_data: dict):
    post = Posts(**post_data)
    session.add(post)
    return post


async def get_posts_for_subscriber(session, subscriber_id):
    data = await session.execute(
        select(Posts).where(
            Posts.creator_id._in(select(UserSubscriptions).where(UserSubscriptions.subscriber_id == subscriber_id))
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
