from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.models.creator import Creator
from common_amirainvest_com.schemas.schema import Users, Securities
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from common_amirainvest_com.utils.decorators import Session


# TO BE USED FOR POSTS / USER SUBSCRIPTIONS
@Session
async def get_creator_attributes(session: AsyncSession, creator_id: UUID):
    data = {
        k: v for k, v in
        (
            await session.execute(select(Users).where(Users.id == creator_id))
        ).scalars().one().dict().items()
        if v is not None
            }
    print(data)
    return Creator(**data)


@Session
async def create_security(session):
    security = {
        "ticker_symbol": "TSLA",
        "close_price": 420.00,
        "open_price": 69.00,
        "name": "T",
    }
    await session.execute(insert(Securities).values(security))


@Session
async def create_user(session):
    user_data = {
        "first_name": "",
        "last_name": "",
        "email": "",
        "username": "",
        "benchmark": 2,
        "sub": ""
    }
    await session.execute(
        insert(Users).values(
            {
                k: v for k, v in user_data.items() if k in Users.__dict__
            }
        )
    )


if __name__ == '__main__':
    from pprint import pprint
    # run_async_function_synchronously(create_user)
    pprint(run_async_function_synchronously(get_creator_attributes, "a29075b1-d6e5-4e6e-9292-349cce606330"))
