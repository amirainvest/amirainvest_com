from sqlalchemy import delete, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.watchlist.model import CreateModel, GetModel, ListModel, UpdateModel
from common_amirainvest_com.schemas.schema import Watchlists
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.generic_utils import calculate_percent_change
from common_amirainvest_com.utils.query_fragments.watchlist_item import watchlist_items_select


@Session
async def create_controller(session: AsyncSession, watchlist_data: CreateModel, creator_id: str):
    watchlist_data_dict = watchlist_data.dict(exclude_none=True)
    watchlist_data_dict["creator_id"] = creator_id
    return (await session.execute(insert(Watchlists).values(**watchlist_data_dict).returning(Watchlists))).fetchone()


@Session
async def get_controller(session: AsyncSession, watchlist_id: int) -> GetModel:
    watchlist_items = []
    watchlist_data = {}
    creator = None
    statement = watchlist_items_select().where(Watchlists.id == watchlist_id)
    for watchlist, watchlist_item, user, security_price, security in (await session.execute(statement)).all():
        watchlist_data = watchlist.dict() if watchlist else None
        creator = user.dict() if user else None
        if watchlist_item:
            watchlist_item = watchlist_item.dict()
            watchlist_item["close_price"] = security.close_price
            watchlist_item["current_price"] = security_price.price
            watchlist_item["percent_change"] = calculate_percent_change(security.close_price, security_price.price)
            watchlist_items.append(watchlist_item)
    return GetModel(
        id=watchlist_data["id"],
        name=watchlist_data["name"],
        created_at=watchlist_data["created_at"],
        updated_at=watchlist_data["updated_at"],
        creator=creator,
        items=watchlist_items,
    )


@Session
async def list_controller(session: AsyncSession, creator_id: str) -> ListModel:
    watchlist_data = {}
    creator = None
    statement = watchlist_items_select().where(Watchlists.creator_id == creator_id)
    for watchlist, watchlist_item, user, security_price, security in (await session.execute(statement)).all():
        creator = user.dict() if user else None
        watchlist = watchlist.dict() if watchlist else None
        watchlist_item = watchlist_item.dict() if watchlist_item else None
        if watchlist is not None:
            if watchlist["id"] not in watchlist_data:
                watchlist_data[watchlist["id"]] = watchlist
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
                    watchlist_item["percent_change"] = calculate_percent_change(
                        security.close_price, security_price.price
                    )
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
