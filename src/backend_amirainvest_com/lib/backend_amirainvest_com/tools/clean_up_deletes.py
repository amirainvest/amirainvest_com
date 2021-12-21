from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import Users
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.generic_utils import get_past_datetime


@Session
async def get_deletable_users(session):
    data = await session.execute(
        select(Users).where(Users.is_deleted is True).where(Users.delted_at > get_past_datetime(days=30))
    )
    return data.scalars().all()


@Session
async def delete_user(session, user_id):
    await session.delete(Users).where(Users.id == user_id)


async def delete_deletable_users():
    deletable_users = await get_deletable_users()
    for user in deletable_users:
        await delete_user(user_id=user.id)
