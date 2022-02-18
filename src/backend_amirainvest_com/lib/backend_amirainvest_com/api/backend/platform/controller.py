import typing as t

from sqlalchemy import insert, update
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.schemas.schema import TwitterUsers, YouTubers, SubstackUsers



async def get_controller(user_id: str) -> t.List[PlatformModel]:
    platforms = []
    twitter = get_twitter_username(user_id)
    if twitter:
        platforms.append(PlatformModel(platform='twitter', username=twitter.username))
    youtube = get_youtube_username(user_id)
    if youtube:
        platforms.append(PlatformModel(platform='youtube', username=youtube.channel_username))
    substack = get_substack_username(user_id)
    if substack:
        platforms.append(PlatformModel(platform='substack', username=substack.username))
    
    if len(platforms) >0:
        return platforms


@Session
async def get_twitter_username(session: AsyncSession, user_id):
    return (
        await (
            session.execute(
                select(TwitterUsers.username)
                .where(TwitterUsers.creator_id == user_id)
            )
        )
    ).one_or_none()


@Session
async def get_substack_username(session: AsyncSession, user_id):
    return (
        await (
            session.execute(
                select(SubstackUsers.username)
                .where(SubstackUsers.creator_id == user_id)
            )
        )
    ).one_or_none()


@Session
async def get_youtube_username(session: AsyncSession, user_id):
    return (
        await (
            session.execute(
                select(YouTubers.channel_username)
                .where(YouTubers.creator_id == user_id)
            )
        )
    ).one_or_none()