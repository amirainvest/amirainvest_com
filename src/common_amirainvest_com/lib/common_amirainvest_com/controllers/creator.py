from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common_amirainvest_com.models.creator import Creator
from common_amirainvest_com.schemas.schema import Users
from common_amirainvest_com.utils.decorators import Session


# TO BE USED FOR POSTS / USER SUBSCRIPTIONS
@Session
async def get_creator_attributes(session: AsyncSession, creator_id: UUID):
    return Creator(
        **{
            k: v
            for k, v in (await session.execute(select(Users).where(Users.id == creator_id)))
            .scalars()
            .one()
            .dict()
            .items()
            if v is not None
        }
    )
