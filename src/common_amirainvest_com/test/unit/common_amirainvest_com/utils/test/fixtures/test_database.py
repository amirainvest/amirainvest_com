pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import Users
from common_amirainvest_com.utils.consts import WEBCACHE


async def test_database_fixture(async_session_maker_test):
    """
    Test to make sure the session is working correctly
    """
    session_test: AsyncSession = async_session_maker_test()

    user_1 = Users(sub="", name="", username="", picture_url="", email="", email_verified=True)
    session_test.add(user_1)
    await session_test.commit()
    assert type(user_1.id) == uuid.UUID

    users = (await session_test.execute(select(Users))).all()
    assert len(users) == 1


async def test_database_fixture_data_deleted_between_tests(async_session_maker_test):
    """
    Test to make sure the test rollback is working correctly and data from other tests is not persisting past function
    run.
    """
    session_test: AsyncSession = async_session_maker_test()

    users = (await session_test.execute(select(Users))).all()
    assert len(users) == 0


async def test_redis_remove_data_part_1():
    WEBCACHE.set(name="test", value="test_value")
    result = WEBCACHE.get("test").decode("UTF-8")
    assert result == "test_value"


async def test_redis_remove_data_part_2():
    result = WEBCACHE.get("test")
    assert result is None
