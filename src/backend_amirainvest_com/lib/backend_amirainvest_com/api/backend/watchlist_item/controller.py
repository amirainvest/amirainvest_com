from typing import List

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.watchlist_item.model import CreateModel, UpdateModel
from common_amirainvest_com.controllers.watchlist import get_watchlist_creator
from common_amirainvest_com.schemas.schema import WatchlistItems
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_controller(session: AsyncSession, watchlist_item_data: CreateModel, creator_id: str):
    assert (await get_watchlist_creator(creator_id=creator_id)) == creator_id
    watchlist_item_data_dict = watchlist_item_data.dict(exclude_none=True)
    return (
        await session.execute(insert(WatchlistItems).values(**watchlist_item_data_dict).returning(WatchlistItems))
    ).fetchone()


@Session
async def get_controller(session: AsyncSession, watchlist_item_id: int) -> WatchlistItems:
    return (
        (await session.execute(select(WatchlistItems).where(WatchlistItems.id == watchlist_item_id)))
        .scalars()
        .one()
        .dict()
    )


@Session
async def list_controller(session: AsyncSession, watchlist_id: int) -> List[WatchlistItems]:
    return [
        x.dict()
        for x in (await session.execute(select(WatchlistItems).where(WatchlistItems.watchlist_id == watchlist_id)))
        .scalars()
        .all()
    ]


@Session
async def update_controller(session: AsyncSession, watchlist_data: UpdateModel, creator_id: str):
    assert (await get_watchlist_creator(creator_id=creator_id)) == creator_id
    return (
        await (
            session.execute(
                update(WatchlistItems)
                .where(WatchlistItems.id == watchlist_data.id)
                .values(**watchlist_data.dict(exclude_none=True))
                .returning(WatchlistItems)
            )
        )
    ).fetchone()


@Session
async def delete_controller(session: AsyncSession, watchlist_item_id: int, creator_id: str) -> None:
    assert (await get_watchlist_creator(creator_id=creator_id)) == creator_id
    await (session.execute(delete(WatchlistItems).where(WatchlistItems.id == watchlist_item_id)))
