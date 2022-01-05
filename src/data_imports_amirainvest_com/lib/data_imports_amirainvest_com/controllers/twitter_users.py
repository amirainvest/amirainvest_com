from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import TwitterUsers
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_twitter_user(session, twitter_user_data: dict):
    twitter_user = TwitterUsers(**twitter_user_data)
    session.add(twitter_user)
    return twitter_user


@Session
async def get_all_twitter_users(session):
    data = await session.execute(select(TwitterUsers))
    return data.scalars().all()
