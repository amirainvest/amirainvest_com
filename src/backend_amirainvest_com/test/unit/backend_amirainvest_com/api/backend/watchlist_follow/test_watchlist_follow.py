import json

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas.schema import WatchlistFollows, Watchlists
from common_amirainvest_com.utils.test.factories.schema import UsersFactory, WatchlistsFactory, WatchlistsFollowsFactory

from ...config import AUTH_HEADERS


async def test_create_watchlist_follow(async_session_maker_test, mock_auth):
    session_test: AsyncSession = async_session_maker_test()
    creator = await UsersFactory()
    follower = await UsersFactory()
    watchlist = await WatchlistsFactory(creator_id=creator.id)
    await mock_auth(follower.id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/create",
            headers=AUTH_HEADERS,
            data=json.dumps({"follower_id": str(follower.id), "watchlist_id": watchlist.id}),
        )
    assert response.status_code == status.HTTP_201_CREATED
    db_watchlist_follow = (
        (await session_test.execute(select(WatchlistFollows).where(WatchlistFollows.follower_id == follower.id)))
        .scalars()
        .one()
    )
    assert str(db_watchlist_follow.follower_id) == str(follower.id)


async def test_get_watchlist_follow(async_session_maker_test, mock_auth):
    creator = await UsersFactory()
    follower = await UsersFactory()
    watchlist = await WatchlistsFactory(creator_id=creator.id)
    watchlist_follow = await WatchlistsFollowsFactory(follower_id=follower.id, watchlist_id=watchlist.id)
    await mock_auth(creator.id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/get",
            headers=AUTH_HEADERS,
            params={"watchlist_follow_id": watchlist_follow.id},
        )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert str(response_data["follower_id"]) == str(watchlist_follow.follower_id)
    assert response_data["watchlist_id"] == watchlist.id


async def test_list_watchlist_follow(async_session_maker_test, mock_auth):
    session_test: AsyncSession = async_session_maker_test()
    creator = await UsersFactory()
    follower = await UsersFactory()
    watchlist_follows = []
    watchlist = await WatchlistsFactory(creator_id=creator.id)
    watchlist_follow = await WatchlistsFollowsFactory(follower_id=follower.id, watchlist_id=watchlist.id)
    watchlist_follows.append(watchlist_follow)
    await mock_auth(follower.id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/list",
            headers=AUTH_HEADERS,
            params={"follower_id": str(follower.id)},
        )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    db_watchlists = [
        x.dict()
        for x in (
            await session_test.execute(
                select(Watchlists, WatchlistFollows).join(Watchlists).where(WatchlistFollows.follower_id == follower.id)
            )
        )
        .scalars()
        .all()
    ]
    assert db_watchlists[0]["id"] == response_data[0]["id"]
    assert db_watchlists[0]["tickers"] == response_data[0]["tickers"]
    assert db_watchlists[0]["name"] == response_data[0]["name"]
    assert db_watchlists[0]["note"] == response_data[0]["note"]


async def test_delete_watchlist_follow(async_session_maker_test, mock_auth):
    session_test: AsyncSession = async_session_maker_test()
    creator = await UsersFactory()
    follower = await UsersFactory()
    watchlist = await WatchlistsFactory(creator_id=creator.id)
    watchlist_follow = await WatchlistsFollowsFactory(follower_id=follower.id, watchlist_id=watchlist.id)
    await mock_auth(creator.id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/delete",
            headers=AUTH_HEADERS,
            params={"watchlist_follow_id": watchlist_follow.id},
        )
    assert response.status_code == status.HTTP_200_OK
    db_watchlist = (
        await session_test.execute(select(WatchlistFollows).where(WatchlistFollows.id == watchlist_follow.id))
    ).one_or_none()
    assert db_watchlist is None
