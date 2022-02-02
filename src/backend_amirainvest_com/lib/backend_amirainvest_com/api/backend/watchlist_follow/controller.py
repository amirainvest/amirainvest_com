import uuid
from typing import List

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.watchlist_follow.model import CreateModel, FollowedWatchlistModel
from common_amirainvest_com.schemas.schema import WatchlistFollows, Watchlists
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_controller(session: AsyncSession, watchlist_follow_data: CreateModel):
    return (
        await session.execute(
            insert(WatchlistFollows).values(**watchlist_follow_data.dict(exclude_none=True)).returning(WatchlistFollows)
        )
    ).fetchone()


@Session
async def get_controller(session: AsyncSession, watchlist_follow_id: int):
    watchlist, watchlist_follow = (
        await session.execute(
            select(Watchlists, WatchlistFollows).join(Watchlists).where(WatchlistFollows.id == watchlist_follow_id)
        )
    ).one()
    return {
        "id": watchlist_follow.id,
        "follower_id": watchlist_follow.follower_id,
        "watchlist_id": watchlist_follow.watchlist_id,
    }


@Session
async def list_controller(session: AsyncSession, follower_id: uuid.UUID) -> List[FollowedWatchlistModel]:
    # GETS FOLLOWERS WATCHLISTS
    return [
        x.dict()
        for x in (
            await session.execute(
                select(Watchlists, WatchlistFollows).join(Watchlists).where(WatchlistFollows.follower_id == follower_id)
            )
        )
        .scalars()
        .all()
    ]


@Session
async def delete_controller(session: AsyncSession, watchlist_follow_id: int) -> None:
    await session.execute(delete(WatchlistFollows).where(WatchlistFollows.id == watchlist_follow_id))
