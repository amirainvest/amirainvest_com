from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import Securities, Users


async def test_database_fixture(async_session_maker_test):
    """
    Test to make sure the session is working correctly
    """
    session_test: AsyncSession = async_session_maker_test()

    benchmark = Securities(ticker_symbol="NA", close_price=0, name="", open_price=0)
    session_test.add(benchmark)
    await session_test.flush()
    user_1 = Users(
        sub="",
        benchmark=benchmark.id,
        first_name="",
        last_name="",
        username="",
        picture_url="",
        email="",
        email_verified=True,
    )
    session_test.add(user_1)
    await session_test.commit()
    assert type(user_1.id) == str

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
