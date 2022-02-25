from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.watchlist.model import CreateModel, GetModel, ListModel, UpdateModel
from common_amirainvest_com.schemas.schema import (
    Users,
    WatchlistItems,
    Watchlists,
    Securities,
    SecurityPrices
)
from common_amirainvest_com.utils.decorators import Session
from decimal import Decimal
from pprint import pprint


def calculate_percent_change(initial_value: Decimal, end_value: Decimal) -> Decimal:
    return 100 * (end_value - initial_value) / initial_value


@Session
async def create_controller(session: AsyncSession, watchlist_data: CreateModel, creator_id: str):
    watchlist_data_dict = watchlist_data.dict(exclude_none=True)
    watchlist_data_dict["creator_id"] = creator_id
    return (await session.execute(insert(Watchlists).values(**watchlist_data_dict).returning(Watchlists))).fetchone()


@Session
async def get_controller(session: AsyncSession, watchlist_id: int) -> GetModel:
    watchlist_items = []
    watchlist_data = None
    creator = None
    statement = (
        select(Watchlists, WatchlistItems, Users, SecurityPrices, Securities)
        .outerjoin(Watchlists, Users.id == Watchlists.creator_id)
        .outerjoin(WatchlistItems, WatchlistItems.watchlist_id == Watchlists.id)
        .outerjoin(Securities, Securities.ticker_symbol == WatchlistItems.ticker)
        .outerjoin(SecurityPrices, SecurityPrices.security_id == Securities.id)
        .where(Watchlists.id == watchlist_id)
    )
    for watchlist, watchlist_item, user, security_price, security in (await session.execute(statement)).all():
        watchlist_data = watchlist.dict() if watchlist else None
        creator = user.dict() if user else None
        if watchlist_item:
            watchlist_item = watchlist_item.dict()
            watchlist_item["close_price"] = security.close_price
            watchlist_item["current_price"] = security_price.price
            watchlist_item["percent_change"] = calculate_percent_change(security.close_price, security_price.price)
            watchlist_items.append(watchlist_item)
    return GetModel(creator=creator, items=watchlist_items, watchlist=watchlist_data)


@Session
async def list_controller(session: AsyncSession, creator_id: str) -> ListModel:
    watchlist_data = {}
    creator = None
    statement = (
        select(Watchlists, WatchlistItems, Users, SecurityPrices, Securities)
        .outerjoin(Watchlists, Users.id == Watchlists.creator_id)
        .outerjoin(WatchlistItems, WatchlistItems.watchlist_id == Watchlists.id)
        .outerjoin(Securities, Securities.ticker_symbol == WatchlistItems.ticker)
        .outerjoin(SecurityPrices, SecurityPrices.security_id == Securities.id)
        .where(Watchlists.creator_id == creator_id)
    )
    for watchlist, watchlist_item, user, security_price, security in (await session.execute(statement)).all():
        creator = user.dict() if user else None
        watchlist = watchlist.dict() if watchlist else None
        watchlist_item = watchlist_item.dict() if watchlist_item else None
        if watchlist is not None:
            if watchlist["id"] not in watchlist_data:
                watchlist_data[watchlist["id"]] = {"watchlist": watchlist}
                if watchlist_item is not None:
                    watchlist_item["close_price"] = security.close_price
                    watchlist_item["current_price"] = security_price.price
                    watchlist_item["percent_change"] = calculate_percent_change(
                        security.close_price, security_price.price
                    )
                    watchlist_data[watchlist["id"]]["items"] = [watchlist_item]
            else:
                if watchlist_item is not None:
                    watchlist_item["close_price"] = security.close_price
                    watchlist_item["current_price"] = security_price.price
                    watchlist_item["percent_change"] = calculate_percent_change(security.close_price, security_price.price)
                    watchlist_data[watchlist["id"]]["items"].append(watchlist_item)
    return ListModel(creator=creator, watchlists=[v for k, v in watchlist_data.items()])


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
        session.execute(delete(Watchlists).where(Watchlists.id == watchlist_id).where(Watchlists.creator_id == user_id))
    )


if __name__ == "__main__":
    from common_amirainvest_com.utils.async_utils import run_async_function_synchronously

    # pprint(run_async_function_synchronously(get_controller, 1).__dict__)
    pprint(run_async_function_synchronously(list_controller, "148c6ef5-ff2e-4b2e-8f66-0c57095a0fb5").__dict__)
