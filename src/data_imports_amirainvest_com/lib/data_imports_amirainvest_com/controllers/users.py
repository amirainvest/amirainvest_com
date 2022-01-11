from functools import lru_cache

from sqlalchemy import select

from common_amirainvest_com.schemas.schema import Users
from common_amirainvest_com.utils.decorators import Session


@Session
@lru_cache(1000)
async def get_user(session, user_id: str):
    return (await session.execute(select(Users).where(Users.id == user_id))).scalars().first()
