from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common_amirainvest_com.schemas.schema import Posts, SubstackArticles, SubstackUsers
from data_imports_amirainvest_com.platforms.substack import load_user_data


async def test_existing_user_upload(async_session_maker_test, factory):
    session_test: AsyncSession = async_session_maker_test()
    username = "saeedjones"
    user = await factory.gen("users")
    await load_user_data(username, user["users"].id)
    await load_user_data(username, user["users"].id)
    assert (await session_test.execute(select(Posts).where(Posts.creator_id == user["users"].id))).all()
    assert (await session_test.execute(select(SubstackUsers).where(SubstackUsers.creator_id == user["users"].id))).all()
    assert (await session_test.execute(select(SubstackArticles).where(SubstackArticles.username == username))).all()
