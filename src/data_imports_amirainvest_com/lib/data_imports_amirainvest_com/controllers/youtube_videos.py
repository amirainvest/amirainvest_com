from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import YouTubeVideos
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_youtube_video(session, youtube_video_data: dict):
    youtube_video = YouTubeVideos(**youtube_video_data)
    session.add(youtube_video)
    return youtube_video


@Session
async def get_videos_for_channel(session, channel_id):
    data = await session.execute(select(YouTubeVideos).where(YouTubeVideos.channel_id == channel_id))
    return data.scalars().all()


@Session
async def get_videos_for_creator(session, creator_id):
    data = await session.execute(select(YouTubeVideos).where(YouTubeVideos.creator_id == creator_id))
    return data.scalars().all()
