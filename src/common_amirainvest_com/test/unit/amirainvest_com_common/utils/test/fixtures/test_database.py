pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common_amirainvest_com.schemas.schema import Users


@pytest.mark.asyncio
async def test_database_fixture(session_test: AsyncSession):
    """
    Test to make sure the session is working correctly
    """
    user_1 = Users(sub="", name="", username="", picture_url="", email="", email_verified=True)
    session_test.add(user_1)
    await session_test.commit()
    assert type(user_1.id) == uuid.UUID

    users = (await session_test.execute(select(Users))).all()
    assert len(users) == 1


@pytest.mark.asyncio
async def test_database_fixture_data_deleted_between_tests(session_test: AsyncSession):
    """
    Test to make sure the test rollback is working correctly and data from other tests is not persisting past function
    run.
    """
    users = (await session_test.execute(select(Users))).all()
    assert len(users) == 0
