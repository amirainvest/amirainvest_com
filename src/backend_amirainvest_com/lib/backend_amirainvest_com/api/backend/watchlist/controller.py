import uuid
from typing import List

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.watchlist.model import CreateModel, UpdateModel
from common_amirainvest_com.schemas.schema import Watchlists
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_controller(session: AsyncSession, watchlist_data: CreateModel) -> Watchlists:
    watchlist = Watchlists(**watchlist_data.dict(exclude_none=True))
    session.add(watchlist)
    return watchlist


@Session
async def get_controller(session: AsyncSession, watchlist_id: int):
    await session.execute(select(Watchlists).where(Watchlists.id == watchlist_id))


@Session
async def list_controller(session: AsyncSession, creator_id: uuid.UUID) -> List[Watchlists]:
    # GETS CREATOR WATCHLISTS
    data = await session.execute(select(Watchlists).where(Watchlists.creator_id == creator_id))
    return data.scalars().all()


@Session
async def update_controller(session: AsyncSession, watchlist_data: UpdateModel) -> Watchlists:
    return (
        await (
            session.execute(
                update(Watchlists)
                .where(Watchlists.id == watchlist_data.id)
                .values(**watchlist_data.dict(exclude_none=True))
                .returning(Watchlists)
            )
        )
    ).one()


@Session
async def delete_controller(session: AsyncSession, watchlist_id: int) -> None:
    await session.execute(delete(Watchlists).where(Watchlists.id == watchlist_id))
