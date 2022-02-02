import uuid
from typing import List

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.watchlist.model import CreateModel, UpdateModel
from common_amirainvest_com.schemas.schema import Watchlists
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_controller(session: AsyncSession, watchlist_data: CreateModel):
    return (
        await session.execute(insert(Watchlists).values(**watchlist_data.dict(exclude_none=True)).returning(Watchlists))
    ).fetchone()


@Session
async def get_controller(session: AsyncSession, watchlist_id: int):
    return (await session.execute(select(Watchlists).where(Watchlists.id == watchlist_id))).scalars().one().dict()


@Session
async def list_controller(session: AsyncSession, creator_id: uuid.UUID) -> List[Watchlists]:
    # GETS CREATOR WATCHLISTS
    return [
        x.dict()
        for x in (await session.execute(select(Watchlists).where(Watchlists.creator_id == creator_id))).scalars().all()
    ]


@Session
async def update_controller(session: AsyncSession, watchlist_data: UpdateModel):
    return (
        await (
            session.execute(
                update(Watchlists)
                .where(Watchlists.id == watchlist_data.id)
                .values(**watchlist_data.dict(exclude_none=True))
                .returning(Watchlists)
            )
        )
    ).fetchone()


@Session
async def delete_controller(session: AsyncSession, watchlist_id: int) -> None:
    await session.execute(delete(Watchlists).where(Watchlists.id == watchlist_id))
