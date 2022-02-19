import asyncio
import typing as t

from sqlalchemy import insert, update, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import parse_obj_as

from backend_amirainvest_com.api.backend.user_route.controller import handle_data_imports
from backend_amirainvest_com.api.backend.platform.model import PlatformModel, CreatePlatformModel
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
            platform, user = await check_twitter_username(p.username)
        elif p.platform == "youtube":
            platform, user = await check_youtube_username(p.username)
        elif p.platform == "substack":
            platform, user = await check_substack_username(p.username)
        
        claimed = user.is_claimed
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
                select(TwitterUsers.username, Users)
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
            select(SubstackUsers.username, Users)
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
                select(YouTubers.channel_username, Users)
                .join(Users)
                .where(YouTubers.channel_username == username)
            )
        )
    ).one_or_none()
    return ({"youtube":youtube}, users)



async def create_platforms(user_id: str, platform_data: t.List[PlatformModel]) -> t.List[CreatePlatformModel]:
    data_import_message = {"creator_id":user_id}
    for p in platform_data:
        if p.platform == "twitter":
            data_import_message["twitter_username"] = p.platform
        elif p.platform == "youtube":
            data_import_message["youtube_channel_id"] = p.platform
        elif p.platform == "substack":
            data_import_message["substack_username"] = p.platform
    handle_data_imports(**data_import_message)
    return parse_obj_as(t.List[CreatePlatformModel], platform_data)

#update husk info
#update subscribers, posts
#generate notifications here, in the controller functions
async def update_after_claim(claimed_platforms: t.List[PlatformModel], user_id: str):
    husk_user_ids = await get_husk_user_id
    pass


async def get_husk_user_id(claimed_platforms:t.List[PlatformModel]) -> t.List:
    husk_user_ids = []
    for p in claimed_platforms:
        if p.platform == "twitter":
            platform, user = await check_twitter_username(p.username)
        elif p.platform == "youtube":
            platform, user = await check_youtube_username(p.username)
        elif p.platform == "substack":
            platform, user = await check_substack_username(p.username)
        
        husk_user_ids.append(
            {
                "platform":platform, 
                "user_id": user.user_id
            }
        )
    return husk_user_ids


@Session
async def update_husk_platforms(session: AsyncSession, claimed_platforms: t.List[PlatformModel], user_id: str):
    pass


@Session
async def update_husk_subscribers(session: AsyncSession, claimed_platforms: t.List[PlatformModel], user_id: str):
    pass


if __name__=="__main__":
    substack, users = asyncio.run(check_substack_username(username='testuser'))
    print(substack, users, users.is_claimed, users.username)