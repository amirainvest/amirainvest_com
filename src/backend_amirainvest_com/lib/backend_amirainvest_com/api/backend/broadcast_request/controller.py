import typing as t

from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import BroadcastRequests
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_controller(session, creator_id: str) -> t.List[BroadcastRequests]:
    data = await session.execute(select(BroadcastRequests).where(BroadcastRequests.creator_id == creator_id))
    return data.scalars().all()


@Session
async def create_controller(session, requester_id: str, creator_id: str) -> BroadcastRequests:
    broadcast_request = BroadcastRequests(
        subscriber_id=requester_id,
        creator_id=creator_id,
    )
    session.add(broadcast_request)
    return broadcast_request
