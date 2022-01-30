import json

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas.schema import WatchlistFollows
from common_amirainvest_com.utils.test.factories.schema import WatchlistsFactory, WatchlistsFollowsFactory, UsersFactory

from ...config import AUTH_HEADERS


async def test_create_watchlist_follow(async_session_maker_test, mock_auth):
    session_test: AsyncSession = async_session_maker_test()
    user = await UsersFactory()
    await mock_auth(user.id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/create",
            headers=AUTH_HEADERS,
            data=json.dumps({"text": "I love your app."}),
        )
    watchlist_follow_data = (await session_test.execute(
        select(WatchlistFollows).where(WatchlistFollows.follower_id == user.id)
    )).scalars().one()
    assert str(watchlist_follow_data.follower_id) == str(user.id)


async def test_get_watchlist_follow(async_session_maker_test, mock_auth):
    session_test: AsyncSession = async_session_maker_test()
    user = await UsersFactory()
    await mock_auth(user.id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/get",
            headers=AUTH_HEADERS,
            data=json.dumps({"text": "I love your app."}),
        )


async def test_list_watchlist_follow(async_session_maker_test, mock_auth):
    session_test: AsyncSession = async_session_maker_test()
    user = await UsersFactory()
    await mock_auth(user.id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/list",
            headers=AUTH_HEADERS,
            data=json.dumps({"text": "I love your app."}),
        )


async def test_delete_watchlist_follow(async_session_maker_test, mock_auth):
    session_test: AsyncSession = async_session_maker_test()
    user = await UsersFactory()
    await mock_auth(user.id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/delete",
            headers=AUTH_HEADERS,
            data=json.dumps({"text": "I love your app."}),
        )
