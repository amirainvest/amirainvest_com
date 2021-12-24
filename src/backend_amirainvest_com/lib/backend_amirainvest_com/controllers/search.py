from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import Posts, Users
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.generic_utils import get_past_datetime


@Session
async def get_all_users(session):
    data = await session.execute(select(Users))
    return data.scalars().all()


@Session
async def get_all_recent_content(session, max_post_hours: int = 48):
    data = await session.execute(select(Posts.text).filter(Posts.created_at > get_past_datetime(hours=max_post_hours)))
    return data.scalars().all()


@Session
async def get_like_content(session, search_term):
    data = await session.execute(
        select(Posts.text).filter(Posts.text.ilike(f"%{search_term.lower()}%")).order_by(Posts.created_at).limit(50)
    )
    return data.scalars().all()


@Session
async def get_like_creator(session, search_term):
    data = await session.execute(select(Users.text).filter(Users.text.ilike(f"%{search_term.lower()}%")).limit(50))
    return data.scalars().all()
