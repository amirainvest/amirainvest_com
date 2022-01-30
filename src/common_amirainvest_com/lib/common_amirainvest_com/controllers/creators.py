import uuid

from common_amirainvest_com.schemas.schema import Users
from common_amirainvest_com.utils.decorators import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@Session
async def get_creator_attributes(session: AsyncSession, creator_id: uuid.UUID):
    return {
        k: v
        for k, v in (await session.execute(select(Users).where(Users.id == creator_id))).scalars().one().dict().items()
        if k in ["id", "name", "username", "picture_url"]
    }
