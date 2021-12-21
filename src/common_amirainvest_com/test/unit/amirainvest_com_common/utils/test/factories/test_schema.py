pytest_plugins = ["amirainvest_com_common.utils.test.fixtures.database"]

import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from amirainvest_com_common.schemas.schema import Users
from amirainvest_com_common.utils.test.factories import schema


@pytest.mark.asyncio
async def test_users_factory(session_test: AsyncSession):
    user_1: Users = await schema.UsersFactory(interests_diversification_rating=42)
    await schema.UsersFactory(interests_diversification_rating=200)

    assert type(user_1.created_at) is datetime.datetime
    assert user_1.interests_diversification_rating == 42

    users = (await session_test.execute(select(Users))).scalars().all()

    assert len(users) == 2


