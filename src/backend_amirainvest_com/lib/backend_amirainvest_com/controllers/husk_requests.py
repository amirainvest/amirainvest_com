from sqlalchemy import delete, select

from common_amirainvest_com.schemas.schema import HuskRequests
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.pydantic_utils import sqlalchemy_to_pydantic


husk_requests_pydantic_model = sqlalchemy_to_pydantic(HuskRequests)


@Session
async def get_husk_requests(session):
    data = await session.execute(select(HuskRequests))
    return data.scalars().all()


@Session
async def create_husk_request(session, husk_request: dict):
    husk_request = HuskRequests(**husk_request)
    session.add(husk_request)
    return husk_request


@Session
async def delete_husk_request(session, husk_request_id):
    await session.execute(delete(HuskRequests).where(HuskRequests.id == husk_request_id))
