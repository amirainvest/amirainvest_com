import asyncio
import typing as t

from sqlalchemy import insert, update, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.platform.model import PlatformModel
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.schemas.schema import TwitterUsers, YouTubers, SubstackUsers, Users



async def get_controller(user_id: str) -> t.List[PlatformModel]:
    platforms = []
    twitter = await get_twitter_username(user_id)
    if twitter:
        platforms.append(PlatformModel(platform='twitter', username=twitter.username))
    youtube = await get_youtube_username(user_id)
    if youtube:
        platforms.append(PlatformModel(platform='youtube', username=youtube.channel_username))
    substack = await get_substack_username(user_id)
    if substack:
        platforms.append(PlatformModel(platform='substack', username=substack.username))
    
    if len(platforms) >0:
        return platforms


@Session
async def get_twitter_username(session: AsyncSession, user_id: str):
    return (
        await (
            session.execute(
                select(TwitterUsers.username)
                .where(TwitterUsers.creator_id == user_id)
                .where(TwitterUsers.is_deleted == False)
            )
        )
    ).one_or_none()


@Session
async def get_substack_username(session: AsyncSession, user_id: str):
    return (
        await (
            session.execute(
                select(SubstackUsers.username)
                .where(SubstackUsers.creator_id == user_id)
                .where(SubstackUsers.is_deleted == False)
            )
        )
    ).one_or_none()


@Session
async def get_youtube_username(session: AsyncSession, user_id: str):
    return (
        await (
            session.execute(
                select(YouTubers.channel_username)
                .where(YouTubers.creator_id == user_id)
                .where(YouTubers.is_deleted == False)
            )
        )
    ).one_or_none()


async def check_platforms(platform_data: t.List[PlatformModel]):
    unclaimed_platforms = []
    claimed_platforms = []
    for p in platform_data:
        if p.platform == "twitter":
            platform, claimed = await check_twitter_username(p.username)
        elif p.platform == "youtube":
            platform, claimed = await check_youtube_username(p.username)
        elif p.platform == "substack":
            platform, claimed = await check_substack_username(p.username)
        
        if claimed:
            claimed_platforms.append(platform)
        else:
            unclaimed_platforms.append(platform)

    return unclaimed_platforms, claimed_platforms


@Session
async def check_twitter_username(session: AsyncSession, username: str):
    twitter, users = (
        await (
            session.execute(
                select(TwitterUsers.username, Uses.is_claimed)
                .join(Users)
                .where(TwitterUsers.username == username)
            )
        )
    ).one_or_none()
    return ({"twitter":twitter}, users)


@Session
async def check_substack_username(session: AsyncSession, username: str):
    substack, users =  (
        await session.execute(
            select(SubstackUsers.username, Users.is_claimed)
            .join(Users)
            .where(SubstackUsers.username == username)
        )
    ).one_or_none()
    return ({"substack":substack}, users)


@Session
async def check_youtube_username(session: AsyncSession, username: str):
    youtube, users = (
        await (
            session.execute(
                select(YouTubers.channel_username, Users.is_claimed)
                .join(Users)
                .where(YouTubers.channel_username == username)
            )
        )
    ).one_or_none()
    return ({"youtube":youtube}, users)


@Session
async def update_after_claim(session: AsyncSession,): #update_claim_data: t.List[UpdateClaimModel]):
    pass


async def create_platforms(user_id: str, platform_data: t.List[PlatformModel]) -> t.List[PlatformModel]:
    pass

@Session
async def create_twitter_user(session: AsyncSession, user_id:str, username: str):
    return


@Session
async def create_substack_user(session: AsyncSession, user_id:str, username: str):
    return


@Session
async def create_youtube_user(session: AsyncSession, user_id:str, username: str):
    return


if __name__=="__main__":
    substack, users = asyncio.run(check_substack_username(username='testuser', claimed=False))
    print(substack, users)