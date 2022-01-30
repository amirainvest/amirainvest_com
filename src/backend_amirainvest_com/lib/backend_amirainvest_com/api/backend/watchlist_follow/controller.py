import uuid
from typing import List

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.watchlist_follow.model import CreateModel
from common_amirainvest_com.schemas.schema import WatchlistFollows, Watchlists
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_controller(session: AsyncSession, watchlist_follow_data: CreateModel) -> WatchlistFollows:
    watchlist_follow = WatchlistFollows(**watchlist_follow_data.dict(exclude_none=True))
    session.add(watchlist_follow)
    return watchlist_follow


@Session
async def get_controller(session: AsyncSession, watchlist_id: int) -> Watchlists:
    return await session.execute(
        select(Watchlists, WatchlistFollows).join(Watchlists).where(Watchlists.id == watchlist_id)
    ).one()


@Session
async def list_controller(session: AsyncSession, follower_id: uuid.UUID) -> List[Watchlists]:
    # GETS FOLLOWERS WATCHLISTS
    return [
        x.dict()
        for x in (
            await session.execute(
                select(Watchlists, WatchlistFollows).join(Watchlists).where(Watchlists.follower_id == follower_id)
            )
        )
        .scalars()
        .all()
    ]


@Session
async def delete_controller(session: AsyncSession, watchlist_follow_id: int) -> None:
    await session.execute(delete(WatchlistFollows).where(WatchlistFollows.id == watchlist_follow_id))
