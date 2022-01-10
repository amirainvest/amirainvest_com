from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import YouTubers
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_youtuber(session, youtuber_data: dict):
    youtuber = YouTubers(**youtuber_data)
    session.add(youtuber)
    return youtuber


@Session
async def get_youtuber(session, channel_id=None, creator_id=None):
    if channel_id:
        data = await session.execute(select(YouTubers).where(YouTubers.channel_id == channel_id))
        return data.scalars().one()
    if creator_id:
        data = await session.execute(select(YouTubers).where(YouTubers.creator_id == creator_id))
        return data.scalars().one()


@Session
async def get_all_youtubers(session):
    data = await session.execute(select(YouTubers))
    return data.scalars().all()
