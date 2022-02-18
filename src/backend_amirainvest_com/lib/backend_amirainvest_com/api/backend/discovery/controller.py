from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.discovery.model import GetModel
from common_amirainvest_com.schemas import schema
from common_amirainvest_com.schemas.schema import Users, UserSubscriptions
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_controller(session: AsyncSession) -> List[GetModel]:
    discovery_profiles = []
    data = (
        await session.execute(
            (
                select(Users, func.count(schema.UserSubscriptions.creator_id).label("subscription_count"))
                .outerjoin(UserSubscriptions, UserSubscriptions.creator_id == Users.id)
                .group_by(UserSubscriptions.id, Users.id)
                .order_by("subscription_count")
            )
        )
    ).all()
    for user, subscription_count in data:
        profile = user.dict()
        profile["subscription_count"] = subscription_count
        discovery_profiles.append(GetModel(**profile))
    return discovery_profiles
