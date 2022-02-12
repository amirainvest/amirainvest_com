from sqlalchemy.ext.asyncio import AsyncSession


async def test_create(async_session_maker_test, factory):
    session_test: AsyncSession = async_session_maker_test()
    user = await factory.gen("users")


