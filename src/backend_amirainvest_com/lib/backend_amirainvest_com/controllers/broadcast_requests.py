import datetime

from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import BroadcastRequests
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_broadcast_request(session, requester_id: str, creator_id: str):
    broadcast_request = BroadcastRequests(
        **{
            "subscriber_id": requester_id,
            "creator_id": creator_id,
            "created_at": datetime.datetime.utcnow(),
        }  # type: ignore
    )
    session.add(broadcast_request)
    return broadcast_request


@Session
async def get_broadcast_requests_for_creator(session, creator_id: str):
    data = await session.execute(select(BroadcastRequests).where(BroadcastRequests.creator_id == creator_id))
    return data.scalars().all()
