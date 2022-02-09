import uuid
from typing import List

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.watchlist.model import CreateModel, UpdateModel
from common_amirainvest_com.schemas.schema import Watchlists
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_controller(session: AsyncSession, watchlist_data: CreateModel, creator_id: str):
    watchlist_data_dict = watchlist_data.dict(exclude_none=True)
    watchlist_data_dict["creator_id"] = creator_id
    return (
        await session.execute(insert(Watchlists).values(**watchlist_data_dict).returning(Watchlists))
    ).fetchone()


@Session
async def get_controller(session: AsyncSession, watchlist_id: int):
    return (await session.execute(select(Watchlists).where(Watchlists.id == watchlist_id))).scalars().one().dict()


@Session
async def list_controller(session: AsyncSession, creator_id: str, user_id: str) -> List[Watchlists]:
    if creator_id == user_id:
        # GETS USERS OWN WATCHLISTS
        return [
            x.dict()
            for x in (await session.execute(select(Watchlists).where(Watchlists.creator_id == user_id))).scalars().all()
        ]
    else:
        # GETS CREATOR WATCHLISTS
        return [
            x.dict()
            for x in (await session.execute(select(Watchlists).where(Watchlists.creator_id == creator_id))).scalars().all()
        ]


@Session
async def update_controller(session: AsyncSession, watchlist_data: UpdateModel, user_id: str):
    return (
        await (
            session.execute(
                update(Watchlists)
                .where(Watchlists.id == watchlist_data.id)
                .where(Watchlists.creator_id == user_id)
                .values(**watchlist_data.dict(exclude_none=True))
                .returning(Watchlists)
            )
        )
    ).fetchone()


@Session
async def delete_controller(session: AsyncSession, watchlist_id: int, user_id: str) -> None:
    await (
        session.execute(
            delete(Watchlists)
            .where(Watchlists.id == watchlist_id)
            .where(Watchlists.creator_id == user_id)
            )
        )
