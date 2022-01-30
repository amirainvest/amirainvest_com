import json

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas.schema import Watchlists
from common_amirainvest_com.utils.test.factories.schema import UsersFactory, WatchlistsFactory

from ...config import AUTH_HEADERS


async def test_create_watchlist(async_session_maker_test, mock_auth):
    session_test: AsyncSession = async_session_maker_test()
    user = await UsersFactory()
    await mock_auth(user.id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "creator_id": str(user.id),
                    "name": "Stocks I should have bought when I was 6",
                    "tickers": ["APPL", "MSFT"]
                }
            ),
        )
    assert response.status_code == 201
    response_data = response.json()
    assert all([x in ["return keys"] for x in response_data])
    watchlist = (await session_test.execute(select(Watchlists).where(Watchlists.creator_id == user.id))).scalars().one()
    assert watchlist


async def test_get_watchlist(async_session_maker_test, mock_auth):
    session_test: AsyncSession = async_session_maker_test()
    user = await UsersFactory()
    watchlist = await WatchlistsFactory(creator_id=user.id)
    await mock_auth(user.id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/get",
            headers=AUTH_HEADERS,
            data=json.dumps({"text": "I love your app."}),
        )


async def test_list_watchlist(async_session_maker_test, mock_auth):
    session_test: AsyncSession = async_session_maker_test()
    user = await UsersFactory()
    watchlists = []
    for x in range(5):
        watchlist = await WatchlistsFactory(creator_id=user.id)
        watchlists.append(watchlist)
    await mock_auth(user.id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/list",
            headers=AUTH_HEADERS,
            data=json.dumps({"text": "I love your app."}),
        )


async def test_update_watchlist(async_session_maker_test, mock_auth):
    session_test: AsyncSession = async_session_maker_test()
    user = await UsersFactory()
    watchlist = await WatchlistsFactory(creator_id=user.id)
    await mock_auth(user.id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/update",
            headers=AUTH_HEADERS,
            data=json.dumps({"text": "I love your app."}),
        )


async def test_delete_watchlist(async_session_maker_test, mock_auth):
    session_test: AsyncSession = async_session_maker_test()
    user = await UsersFactory()
    watchlist = await WatchlistsFactory(creator_id=user.id)
    await mock_auth(user.id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/delete",
            headers=AUTH_HEADERS,
            data=json.dumps({"id": watchlist.id}),
        )
