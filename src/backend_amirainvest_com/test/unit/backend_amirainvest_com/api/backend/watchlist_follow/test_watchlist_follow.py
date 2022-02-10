import json

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas.schema import WatchlistFollows, Watchlists

from ...config import AUTH_HEADERS


# factory.gen doesn't work for watchlists. Keyerror with sql alchemy array
@pytest.mark.skip
async def test_create_watchlist_follow(async_session_maker_test, mock_auth, factory):
    session_test: AsyncSession = async_session_maker_test()
    creator = await factory.gen("users")
    follower = await factory.gen("users")
    watchlist = await factory.gen("watchlists", {"watchlists": {"creator_id": creator["users"].id}})
    await mock_auth(follower["users"].id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/create",
            headers=AUTH_HEADERS,
            data=json.dumps({"follower_id": str(follower["users"].id), "watchlist_id": watchlist["watchlists"].id}),
        )
    assert response.status_code == status.HTTP_201_CREATED
    db_watchlist_follow = (
        (
            await session_test.execute(
                select(WatchlistFollows).where(WatchlistFollows.follower_id == follower["users"].id)
            )
        )
        .scalars()
        .one()
    )
    assert str(db_watchlist_follow.follower_id) == str(follower["users"].id)


@pytest.mark.skip
async def test_get_watchlist_follow(async_session_maker_test, mock_auth, factory):
    creator = await factory.gen("users")
    # follower = await factory.gen("users")
    watchlist = await factory.gen("watchlists", {"watchlists": {"creator_id": creator["users"].id}})
    watchlist_follow = await factory.gen(
        "watchlist_follows", {"watchlist_follows": {"creator_id": creator["users"].id}}
    )
    await mock_auth(creator["users"].id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/get",
            headers=AUTH_HEADERS,
            params={"watchlist_follow_id": watchlist_follow["watchlist_follows"].id},
        )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert str(response_data["follower_id"]) == str(watchlist_follow["watchlist_follows"].id)
    assert response_data["watchlist_id"] == watchlist["watchlist"].id


@pytest.mark.skip
async def test_list_watchlist_follow(async_session_maker_test, mock_auth, factory):
    session_test: AsyncSession = async_session_maker_test()
    creator = await factory.gen("users")
    follower = await factory.gen("users")
    watchlist_follows = []
    # watchlist = await factory.gen("watchlists", {"watchlists": {"creator_id": creator["users"].id}})
    watchlist_follow = await factory.gen(
        "watchlist_follows", {"watchlist_follows": {"creator_id": creator["users"].id}}
    )
    watchlist_follows.append(watchlist_follow)
    await mock_auth(follower["users"].id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/list",
            headers=AUTH_HEADERS,
            params={"follower_id": str(follower["users"].id)},
        )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    db_watchlists = [
        x.dict()
        for x in (
            await session_test.execute(
                select(Watchlists, WatchlistFollows)
                .join(Watchlists)
                .where(WatchlistFollows.follower_id == follower["users"].id)
            )
        )
        .scalars()
        .all()
    ]
    assert db_watchlists[0]["id"] == response_data[0]["id"]
    assert db_watchlists[0]["tickers"] == response_data[0]["tickers"]
    assert db_watchlists[0]["name"] == response_data[0]["name"]
    assert db_watchlists[0]["note"] == response_data[0]["note"]


@pytest.mark.skip
async def test_delete_watchlist_follow(async_session_maker_test, mock_auth, factory):
    session_test: AsyncSession = async_session_maker_test()
    creator = await factory.gen("users")
    follower = await factory.gen("users")
    watchlist = await factory.gen("watchlists", {"watchlists": {"creator_id": creator["users"].id}})
    watchlist_follow = await factory.gen(
        "watchlist_follows",
        {"watchlist_follows": {"follower_id": follower["users"].id, "watchlist_id": watchlist["watchlist"].id}},
    )
    await mock_auth(creator["users"].id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_follow/delete",
            headers=AUTH_HEADERS,
            params={"watchlist_follow_id": watchlist_follow["watchlist_follows"].id},
        )
    assert response.status_code == status.HTTP_200_OK
    db_watchlist = (
        await session_test.execute(
            select(WatchlistFollows).where(WatchlistFollows.id == watchlist_follow["watchlist_follows"].id)
        )
    ).one_or_none()
    assert db_watchlist is None
