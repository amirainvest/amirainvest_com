from datetime import datetime

from sqlalchemy import delete, insert, select, update
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.watchlist.model import CreateModel, GetModel, ListModel, UpdateModel
from common_amirainvest_com.schemas.schema import Users, Watchlists, SecurityPrices, Securities
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
    statement = statement.where(SecurityPrices.price_time == datetime(datetime.today().year, datetime.today().month,datetime.today().day-1, 21,0,0,0))
    sub_q1 = select(Securities.id, max(SecurityPrices.price_time)).outerjoin(SecurityPrices, SecurityPrices.security_id == Securities.id).where(Securities.id == 24)
    print((await session.execute(sub_q1)).all())
    for watchlist, watchlist_item, user, security_price, security in (await session.execute(statement)).all():
        watchlist_data = watchlist.dict() if watchlist else None
        creator = user.dict() if user else None
        if watchlist_item:
            watchlist_item = watchlist_item.dict()
            watchlist_item["close_price"] = security.close_price
            watchlist_item["current_price"] = security_price.price
            if security.close_price == 0:
                watchlist_item["percent_change"] = 0
            else:
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
    statement = sa.text("""select watchlists.name as name, watchlist_items.watchlist_id as id, count(watchlist_items.id) as num_items, watchlists.created_at, watchlists.updated_at
                            from watchlists
                            left join watchlist_items
                            on watchlist_items.watchlist_id = watchlists.id
                            where watchlists.creator_id = '{0}'
                            group by watchlists.creator_id, watchlists.name, watchlist_items.watchlist_id, watchlists.created_at, watchlists.updated_at
                            """.format(creator_id))
    watchlist_data = [x._asdict() for x in (await session.execute(statement)).all()]
    print(watchlist_data)

    if creator is None:
        creator = (await session.execute(select(Users).where(Users.id == creator_id))).scalars().one().dict()
    return ListModel(creator=creator, watchlists=watchlist_data)


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
