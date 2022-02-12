from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common_amirainvest_com.schemas.schema import YouTubers, YouTubeVideos
from data_imports_amirainvest_com.platforms.youtube import load_user_data


async def test_existing_user_upload(async_session_maker_test, factory):
    session_test: AsyncSession = async_session_maker_test()
    user = await factory.gen("users")
    channel_id = "UCPE_2uAJztDd1MYDEusls8Q"  # Coty Fivecoat Channel
    await load_user_data(channel_id, user["users"].id)
    await load_user_data(channel_id, user["users"].id)
    assert (
        (await session_test.execute(select(YouTubers).where(YouTubers.creator_id == user["users"].id))).scalars().all()
    )
    assert (
        (await session_test.execute(select(YouTubeVideos).where(YouTubeVideos.channel_id == channel_id)))
        .scalars()
        .all()
    )
