from typing import List

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from backend_amirainvest_com.api.backend.watchlist_follow.model import CreateModel, WatchlistAttributesModel

from common_amirainvest_com.schemas.schema import WatchlistFollows, Watchlists
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_controller(session: AsyncSession, watchlist_follow_data: CreateModel, user_id: str):
    watchlist_follow_data_dict = watchlist_follow_data.dict(exclude_none=True)
    watchlist_follow_data_dict["follower_id"] = user_id
    return (
        await session.execute(insert(WatchlistFollows).values(**watchlist_follow_data_dict).returning(WatchlistFollows))
    ).fetchone()


@Session
async def get_controller(session: AsyncSession, watchlist_follow_id: int, user_id: str):
    watchlist, watchlist_follow = (
        await session.execute(
            select(Watchlists, WatchlistFollows)
            .join(Watchlists)
            .where(WatchlistFollows.id == watchlist_follow_id)
            .where(WatchlistFollows.follower_id == user_id)
        )
    ).one()
    return {
        "id": watchlist_follow.id,
        "follower_id": watchlist_follow.follower_id,
        "watchlist_id": watchlist_follow.watchlist_id,
    }


@Session
async def list_controller(session: AsyncSession, user_id: str) -> List[WatchlistAttributesModel]:
    # GETS FOLLOWERS WATCHLISTS
    statement = sa.text("""select watchlist_follows.watchlist_id as id, T.name, T.num_items, T.created_at, T.updated_at
                        from watchlist_follows
                        left join
                        (select watchlists.name as name, watchlists.id as id, count(watchlist_items.id) as num_items, watchlists.created_at, watchlists.updated_at
                        from watchlists
                        left join watchlist_items
                        on watchlist_items.watchlist_id = watchlists.id
                        group by watchlists.creator_id, watchlists.name, watchlists.id, watchlists.created_at, watchlists.updated_at) as T
                        on T.id = watchlist_follows.watchlist_id
                        where watchlist_follows.follower_id = '{0}'""".format(user_id))

    watchlist_data = [x._asdict() for x in (await session.execute(statement)).all()]

    return watchlist_data


@Session
async def delete_controller(session: AsyncSession, watchlist_id: int, user_id: str) -> None:
    await session.execute(
        delete(WatchlistFollows)
        .where(WatchlistFollows.watchlist_id == watchlist_id)
        .where(WatchlistFollows.follower_id == user_id)
    )
