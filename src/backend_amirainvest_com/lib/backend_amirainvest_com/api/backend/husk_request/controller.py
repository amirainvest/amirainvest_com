import typing as t

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.backend.husk_request.model import CreateModel
from common_amirainvest_com.schemas.schema import HuskRequests
from common_amirainvest_com.utils.decorators import Session


@Session
async def list_controller(session: AsyncSession) -> t.List[HuskRequests]:
    data = await session.execute(select(HuskRequests))
    return data.scalars().all()


@Session
async def create_controller(session: AsyncSession, husk_request_data: CreateModel) -> HuskRequests:
    husk_request = HuskRequests(**husk_request_data.dict(exclude_none=True))
    session.add(husk_request)
    return husk_request


@Session
async def delete_controller(session: AsyncSession, husk_request_id: int) -> None:
    await session.execute(delete(HuskRequests).where(HuskRequests.id == husk_request_id))
