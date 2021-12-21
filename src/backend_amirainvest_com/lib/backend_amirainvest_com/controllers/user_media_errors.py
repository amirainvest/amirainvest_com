from sqlalchemy import select

from common_amirainvest_com.schemas.schema import UserMediaErrors
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.pydantic_utils import sqlalchemy_to_pydantic


user_media_errors_pydantic_model = sqlalchemy_to_pydantic(UserMediaErrors)


@Session
async def create_user_media_error(session, user_media_error_data: dict):
    user_media_error = UserMediaErrors(**user_media_error_data)
    session.add(user_media_error)
    return user_media_error


@Session
async def get_user_media_errors(session):
    user_media_error = await session.execute(select(UserMediaErrors))
    return user_media_error
