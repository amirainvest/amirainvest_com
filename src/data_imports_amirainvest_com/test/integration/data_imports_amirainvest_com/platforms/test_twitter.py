import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common_amirainvest_com.schemas.schema import Posts, Tweets, TwitterUsers
from data_imports_amirainvest_com.platforms.twitter import load_user_data


@pytest.mark.skip
async def test_existing_user_upload(async_session_maker_test, factory):
    session_test: AsyncSession = async_session_maker_test()
    twitter_handle = "CotyFivecoat"
    user = await factory.gen("users")
    await load_user_data(twitter_handle, user["users"].id)
    await load_user_data(twitter_handle, user["users"].id)
    assert (await session_test.execute(select(Posts).where(Posts.creator_id == user["users"].id))).all()
    twitter_user = (
        (await session_test.execute(select(TwitterUsers).where(TwitterUsers.creator_id == user["users"].id)))
        .scalars()
        .one()
    )
    assert twitter_user
    assert (
        await session_test.execute(select(Tweets).where(Tweets.twitter_user_id == twitter_user.twitter_user_id))
    ).all()
