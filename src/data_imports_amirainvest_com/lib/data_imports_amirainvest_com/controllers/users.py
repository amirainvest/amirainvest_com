from sqlalchemy import select

from common_amirainvest_com.schemas.schema import Users
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_user(session, user_id: str):
    return (await session.execute(select(Users).where(Users.id == user_id))).scalars().first()
