import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import Posts, Users
from common_amirainvest_com.utils.test.factories import schema


async def test_users_factory(async_session_maker_test, factory):
    session_test: AsyncSession = async_session_maker_test()

    # security = await schema.SecuritiesFactory()
    # user_1: Users = await schema.UsersFactory(interests_diversification_rating=42, benchmark=security.id)
    # await schema.UsersFactory(interests_diversification_rating=200, benchmark=security.id)

    user_1 = await factory.gen("users")
    await factory.gen("users")

    assert type(user_1.created_at) is datetime.datetime
    assert user_1.interests_diversification_rating == 42

    users = (await session_test.execute(select(Users))).scalars().all()

    assert len(users) == 2


async def test_posts_factory(async_session_maker_test):
    session_test: AsyncSession = async_session_maker_test()

    security = await schema.SecuritiesFactory()
    user_1: Users = await schema.UsersFactory(benchmark=security.id)
    await schema.PostsFactory(creator_id=user_1.id)

    posts = (await session_test.execute(select(Posts))).scalars().all()

    assert len(posts) == 1
