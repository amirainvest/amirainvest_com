from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import SubstackUsers
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_substack_user(session, substack_user_data: dict):
    substack_user = SubstackUsers(**substack_user_data)
    session.add(substack_user)
    return substack_user


@Session
async def get_substack_user_creator_id():
    pass


@Session
async def get_all_substack_users(session):
    data = await session.execute(select(SubstackUsers))
    return data.scalars().all()
