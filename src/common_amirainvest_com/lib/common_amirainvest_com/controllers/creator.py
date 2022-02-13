from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common_amirainvest_com.models.creator import Creator
from common_amirainvest_com.schemas.schema import Users
from common_amirainvest_com.utils.decorators import Session


# TO BE USED FOR POSTS / USER SUBSCRIPTIONS
@Session
async def get_creator_attributes(session: AsyncSession, creator_id: str):
    user = (await session.execute(select(Users).where(Users.id == creator_id))).scalars().one()
    creator_data = {k: v for k, v in user.dict().items() if v is not None}
    return Creator(
        id=creator_data.get("id"),
        first_name=creator_data.get("first_name"),
        last_name=creator_data.get("last_name"),
        username=creator_data.get("username"),
        picture_url=creator_data.get("picture_url"),
        chip_labels=creator_data.get("chip_labels"),
    )
