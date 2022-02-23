import asyncio
import typing as t

from sqlalchemy import update, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from pydantic import parse_obj_as
#from fastapi import HTTPException, status

from backend_amirainvest_com.api.backend.user_route.controller import handle_data_imports
from backend_amirainvest_com.api.backend.platform.model import PlatformModel, CreatePlatformModel
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.schemas.schema import TwitterUsers, YouTubers, SubstackUsers, Users, BroadcastRequests, UserSubscriptions, Posts



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
    count = 0
    for p in platform_data:
        count += 1
        if p.platform.value == "twitter":
            response = await check_twitter_username(p.username)
        elif p.platform.value == "youtube":
            response= await check_youtube_username(p.username)
        elif p.platform.value == "substack":
            response= await check_substack_username(p.username)
        
        if response:
            # TODO: can just pass p, not remake the platform dict
            platform, user = response
            claimed_platforms.append(platform) if user.is_claimed else unclaimed_platforms.append(platform)

    return claimed_platforms, unclaimed_platforms


@Session
async def check_twitter_username(session: AsyncSession, username: str):
    response = (
        await (
            session.execute(
                select(TwitterUsers.username, Users)
                .join(Users)
                .where(TwitterUsers.username == username)
            )
        )
    ).one_or_none()
    if response:
        twitter_username, users = response
        return ({"platform":"twitter", "username":twitter_username}, users)

    


@Session
async def check_substack_username(session: AsyncSession, username: str):
    response =  (
        await session.execute(
            select(SubstackUsers.username, Users)
            .join(Users)
            .where(SubstackUsers.username == username)
        )
    ).one_or_none()
    if response:
        substack_username, users = response
        return ({"platform":"substack","username":substack_username}, users)


@Session
async def check_youtube_username(session: AsyncSession, username: str):
    response = (
        await (
            session.execute(
                select(YouTubers.channel_username, Users)
                .join(Users)
                .where(YouTubers.channel_username == username)
            )
        )
    ).one_or_none()
    if response:
        youtube_channel, users = response
        return ({"platform":"youtube", "username":youtube_channel}, users)



async def create_platforms(user_id: str, platform_data: t.List[PlatformModel]) -> t.List[CreatePlatformModel]:
    data_import_message = {"creator_id":user_id, "expedited":True}
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
#update subscribers
#update posts
#generate notifications here, in the controller functions
async def claim_platforms(claimed_platforms: t.List[PlatformModel], user_id: str):
    husk_platform_ids = await get_husk_platform_user_id(claimed_platforms)
    await update_husk_platforms(user_id, husk_platform_ids)
    await update_husk_posts(user_id, husk_platform_ids)
    unique_husk_user_ids = await check_husk_user_ids_unique(husk_platform_ids)
    husk_subscribers = await get_husk_broadcast_requests(unique_husk_user_ids)
    await update_husk_subscribers(user_id, husk_subscribers)
    #await generate_notifications()
    claimed = parse_obj_as(t.List[CreatePlatformModel], claimed_platforms)
    for p in claimed:
        p.is_claimed = True
    return claimed


async def check_husk_user_ids_unique(husk_user_ids: t.List) -> t.List:
    unique_ids = set()
    for husk in husk_user_ids:
        unique_ids.add(husk["user_id"])
    return list(unique_ids)



async def get_husk_platform_user_id(claimed_platforms:t.List[PlatformModel]) -> t.List:
    husk_user_ids = []
    for p in claimed_platforms:
        if p.platform.value == "twitter":
            platform, user = await check_twitter_username(p.username)
        elif p.platform.value == "youtube":
            platform, user = await check_youtube_username(p.username)
        elif p.platform.value == "substack":
            platform, user = await check_substack_username(p.username)

        husk_user_ids.append(
            {
                "platform":platform["platform"], 
                "user_id": user.id
            }
        )
    return husk_user_ids


async def update_husk_platforms(user_id: str, husk_platform_ids: t.List):
    for h in husk_platform_ids:
        if h['platform'] == "twitter":
            await update_twitter_user_id(h["user_id"], user_id)
        elif h['platform'] == "youtube":
            await update_youtuber_id(h["user_id"], user_id)
        elif h['platform'] == "substack":
            await update_substack_user_id(h["user_id"], user_id)


@Session
async def update_twitter_user_id(session: AsyncSession, husk_user_id: str, user_id: str):
    await session.execute(
        update(TwitterUsers)
        .where(TwitterUsers.creator_id == husk_user_id)
        .values({"creator_id":user_id})
    )

@Session
async def update_youtuber_id(session: AsyncSession, husk_user_id: str, user_id: str):
    await session.execute(
        update(YouTubers)
        .where(YouTubers.creator_id == husk_user_id)
        .values({"creator_id":user_id})
    )

@Session
async def update_substack_user_id(session: AsyncSession, husk_user_id: str, user_id: str):
    await session.execute(
        update(SubstackUsers)
        .where(SubstackUsers.creator_id == husk_user_id)
        .values({"creator_id": user_id})
    )

@Session
async def update_husk_posts(session: AsyncSession, user_id: str, husk_platform_ids: t.List):
    for p in husk_platform_ids:
        await session.execute(
            update(Posts)
            .where(Posts.creator_id == p["user_id"])
            .where(Posts.platform == p["platform"])
            .values({"creator_id": user_id})
        )

@Session
async def get_husk_broadcast_requests(session: AsyncSession, husk_unique_ids: t.List) ->t.List:
    unique_requests = []
    for husk_id in husk_unique_ids:
        requests = (await session.execute(
            select(BroadcastRequests.subscriber_id)
            .where(BroadcastRequests.creator_id == husk_id)
        )).all()
        temp = {
            "husk_id":husk_id,
            "unique_requests":list(set([x[0] for x in requests]))
        }
        unique_requests.append(temp) 
    return unique_requests

@Session
async def update_husk_subscribers(session: AsyncSession, user_id: str, husk_subscribers: t.List):
    updated_subscriptions = []
    for husk in husk_subscribers:
        await session.execute(
            update(UserSubscriptions)
            .where(UserSubscriptions.creator_id == husk["husk_id"])
            .where(UserSubscriptions.subscriber_id.in_(husk["unique_requests"]))
            .values({"creator_id":user_id})
        )

        vals = [{"subscriber_id":x, "creator_id":user_id} for x in husk["unique_requests"]]
        print(vals)
        stmt = insert(UserSubscriptions).values(vals)
        stmt = stmt.on_conflict_do_nothing(constraint="uq_user_sub")
        await session.execute(stmt)
        



if __name__=="__main__":
    platform, user = asyncio.run(check_twitter_username('testuser'))
    print("platform", platform)
    print("user:", user)
    print(user.is_claimed)    
        
        #update_husk_subscribers('8133ef39-5df5-4e35-a127-629309e53828', [{'husk_id': '8133ef39-5df5-4e35-a127-629309e53890', 'unique_requests': ['8133ef39-5df5-4e35-a127-629309e66666', '8133ef39-5df5-4e35-a127-629309e55555']}]))
