from sqlalchemy import delete
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import HuskRequests
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_husk_requests(session):
    data = await session.execute(select(HuskRequests))
    return data.scalars().all()


@Session
async def create_husk_request(session, husk_request_data: dict):
    husk_request = HuskRequests(**husk_request_data)
    session.add(husk_request)
    return husk_request


@Session
async def delete_husk_request(session, husk_request_id):
    await session.execute(delete(HuskRequests).where(HuskRequests.id == husk_request_id))
