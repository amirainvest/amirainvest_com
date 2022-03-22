from sqlalchemy import delete, insert, select, update, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.watchlist.model import CreateModel, GetModel, ListModel, UpdateModel
from common_amirainvest_com.schemas.schema import Users, Watchlists
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_controller(session: AsyncSession, watchlist_data: CreateModel, creator_id: str):
    watchlist_data_dict = watchlist_data.dict(exclude_none=True)
    watchlist_data_dict["creator_id"] = creator_id
    return (await session.execute(insert(Watchlists).values(**watchlist_data_dict).returning(Watchlists))).fetchone()


@Session
async def get_controller(session: AsyncSession, watchlist_id: int) -> GetModel:

    statement = text(
        """select watchlist_items.id as id ,watchlist_items.ticker as ticker,
                            watchlist_items.note as note, current_price, close_price,
                            case close_price when 0 then 0 else (current_price-close_price)/close_price end
                            as percent_change
                            from watchlist_items
                            left join
                            (select securities.id as sec_id, securities.ticker_symbol as ticker,
                            security_prices.price_time as timestamp, security_prices.price as current_price,
                            securities.close_price as close_price
                            from securities
                            left join security_prices on security_prices.security_id = securities.id
                            where (securities.id,security_prices.price_time) in
                            (select securities.id, max(security_prices.price_time)
                            from securities
                            left join security_prices on security_prices.security_id = securities.id
                            group by securities.id)) as Q
                            on Q.ticker = watchlist_items.ticker
                            where watchlist_id = {0}""".format(
            watchlist_id
        )
    )

    watchlist_items = [x._asdict() for x in (await session.execute(statement)).all()]

    watchlist_data = (
        (await session.execute(select(Watchlists).where(
        Watchlists.id == watchlist_id)))
        .scalars()
        .one_or_none()
        .dict()
    )

    creator = (
        (await session.execute(select(Users).where(Users.id == str(watchlist_data["creator_id"]))))
        .scalars()
        .one()
        .dict()
    )

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

    creator = None
    statement = text(
        """select watchlists.name as name, watchlists.id as id, count(watchlist_items.id) as num_items,
                             watchlists.created_at, watchlists.updated_at
                            from watchlists
                            left join watchlist_items
                            on watchlist_items.watchlist_id = watchlists.id
                            where watchlists.creator_id = '{0}'
                            group by watchlists.creator_id, watchlists.name, watchlists.id, watchlists.created_at,
                            watchlists.updated_at
                            """.format(
            creator_id
        )
    )
    watchlist_data = [x._asdict() for x in (await session.execute(statement)).all()]

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
