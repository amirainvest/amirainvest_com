from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common_amirainvest_com.schemas.schema import WatchlistItems, Watchlists
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_watchlist_creator(
    session: AsyncSession, creator_id: Optional[int] = None, watchlist_item_id: Optional[int] = None
) -> Optional[str]:
    if creator_id:
        return (
            (await session.execute(select(Watchlists.creator_id).where(Watchlists.creator_id == creator_id)))
            .scalars()
            .one()
        )
    if watchlist_item_id:
        return (
            (
                await session.execute(
                    (
                        select(Watchlists.creator_id)
                        .join(WatchlistItems, Watchlists.id == WatchlistItems.watchlist_id)
                        .where(WatchlistItems.id == watchlist_item_id)
                    )
                )
            )
            .scalars()
            .one()
        )
    return None
