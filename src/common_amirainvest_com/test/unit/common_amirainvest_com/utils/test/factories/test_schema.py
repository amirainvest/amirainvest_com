import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import Bookmarks, Posts, Users


async def test_users_factory(async_session_maker_test, factory):
    session_test: AsyncSession = async_session_maker_test()

    user_1 = await factory.gen("users", {"users": {"interests_diversification_rating": 42}})
    await factory.gen("users")

    assert type(user_1["users"].created_at) is datetime.datetime
    assert user_1["users"].interests_diversification_rating == 42

    users = (await session_test.execute(select(Users))).scalars().all()

    assert len(users) == 2


async def test_posts_factory(async_session_maker_test, factory):
    session_test: AsyncSession = async_session_maker_test()

    await factory.gen("posts")

    posts = (await session_test.execute(select(Posts))).scalars().all()
    users = (await session_test.execute(select(Users))).scalars().all()

    assert len(users) == 1
    assert len(posts) == 1


@pytest.mark.skip
async def test_bookmarks_factory(async_session_maker_test, factory):
    session_test: AsyncSession = async_session_maker_test()

    await factory.gen("bookmarks")

    posts = (await session_test.execute(select(Posts))).scalars().all()
    bookmarks = (await session_test.execute(select(Bookmarks))).scalars().all()
    users = (await session_test.execute(select(Users))).scalars().all()

    assert len(users) == 2
    assert len(bookmarks) == 1
    assert len(posts) == 1
