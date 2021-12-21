from common_amirainvest_com.schemas.schema import TwitterUsers
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.pydantic_utils import sqlalchemy_to_pydantic


twitter_users_pydantic_model = sqlalchemy_to_pydantic(TwitterUsers)


@Session
async def create_twitter_user(session, twitter_user_data: dict):
    twitter_user = TwitterUsers(**twitter_user_data)
    session.add(twitter_user)
    return twitter_user
