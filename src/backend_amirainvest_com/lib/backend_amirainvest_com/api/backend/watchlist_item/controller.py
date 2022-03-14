from typing import List, Optional

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.watchlist_item.model import CreateModel, UpdateModel
from common_amirainvest_com.schemas.schema import WatchlistItems, Watchlists, Securities
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_controller(session: AsyncSession, watchlist_item_data: CreateModel):
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
async def update_controller(session: AsyncSession, watchlist_data: UpdateModel):
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
async def delete_controller(session: AsyncSession, watchlist_item_id: int) -> None:
    await (session.execute(delete(WatchlistItems).where(WatchlistItems.id == watchlist_item_id)))


@Session
async def passable_ticker(session: AsyncSession, ticker: str, watchlist_id: Optional[int] = None) -> int:
    tickers = (await (session.execute(
        select(WatchlistItems.ticker)
        .join(Watchlists)
        .where(Watchlists.id == watchlist_id)
    ))).scalars().all()
    if ticker in tickers:
        return 1
    
    total_tickers = (
        await (session.execute(select(Securities.ticker_symbol)))).scalars().all()
    if ticker not in total_tickers:
        return 0
    
    return 2