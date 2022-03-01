import itertools
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
                .where(Users.trading_strategies.isnot(None))  # type: ignore
                .where(Users.public_profile_deactivate != True)  # noqa
                .where(Users.is_deleted.is_(False))
                .where(Users.is_deactivated.is_(False))
                .outerjoin(UserSubscriptions, UserSubscriptions.creator_id == Users.id)
                .group_by(UserSubscriptions.id, Users.id)
                .order_by("subscription_count")
            )
        )
    ).all()
    for user, subscription_count in data:
        user = user.dict()
        discovery_profiles.append(
            {
                "creator": user,
                "subscription_count": subscription_count,
                "trading_strategy": user["trading_strategies"][0] if user["trading_strategies"] else "",
            }
        )
    discovery_profiles = sorted(discovery_profiles, key=lambda x: x["trading_strategy"])
    return [
        GetModel(**{"trading_strategy": trading_strategy, "values": list(values)})
        for trading_strategy, values in itertools.groupby(discovery_profiles, key=lambda x: x["trading_strategy"])
    ]
