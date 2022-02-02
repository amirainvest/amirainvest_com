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
            "/watchlist/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "creator_id": str(user.id),
                    "name": "Stocks I should have bought when I was 6",
                    "tickers": ["APPL", "MSFT"],
                }
            ),
        )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    watchlist = (await session_test.execute(select(Watchlists).where(Watchlists.creator_id == user.id))).scalars().one()
    assert str(watchlist.creator_id) == str(response_data["creator_id"])
    assert watchlist.name == "Stocks I should have bought when I was 6"
    assert all([x in watchlist.tickers for x in ["APPL", "MSFT"]])
    db_watchlist = (await session_test.execute(select(Watchlists).where(Watchlists.id == watchlist.id))).scalars().one()
    assert db_watchlist
    assert db_watchlist.id == watchlist.id


async def test_get_watchlist(mock_auth):
    user = await UsersFactory()
    watchlist = await WatchlistsFactory(creator_id=user.id)
    await mock_auth(user.id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist/get",
            headers=AUTH_HEADERS,
            params={"watchlist_id": watchlist.id},
        )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data
    assert str(response_data["creator_id"]) == str(user.id)
    assert response_data["name"] == watchlist.name
    assert response_data["tickers"] == watchlist.tickers


async def test_list_watchlist(async_session_maker_test, mock_auth):
    user = await UsersFactory()
    watchlists = []
    for x in range(5):
        watchlist = await WatchlistsFactory(creator_id=user.id)
        watchlists.append(watchlist)
    await mock_auth(user.id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/watchlist/list", headers=AUTH_HEADERS, params={"creator_id": str(user.id)})
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data
    assert len(response_data) == 5
    assert type(response_data) == list


async def test_update_watchlist(async_session_maker_test, mock_auth):
    session_test: AsyncSession = async_session_maker_test()
    user = await UsersFactory()
    watchlist = await WatchlistsFactory(creator_id=user.id)
    await mock_auth(user.id)
    watchlist_update_dict = {
        "id": watchlist.id,
        "name": "Updated Name",
        "tickers": ["SPY", "VOO"],
        "note": "Updated String",
    }
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist/update",
            headers=AUTH_HEADERS,
            data=json.dumps(watchlist_update_dict),
        )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    for key in response_data:
        if key in watchlist_update_dict:
            assert response_data[key] == watchlist_update_dict[key]
    db_watchlist = (await session_test.execute(select(Watchlists).where(Watchlists.id == watchlist.id))).scalars().one()
    assert db_watchlist.id == watchlist.id
    assert db_watchlist.name == watchlist_update_dict["name"]
    assert db_watchlist.tickers == watchlist_update_dict["tickers"]
    assert db_watchlist.note == watchlist_update_dict["note"]


async def test_delete_watchlist(async_session_maker_test, mock_auth):
    session_test: AsyncSession = async_session_maker_test()
    user = await UsersFactory()
    watchlist = await WatchlistsFactory(creator_id=user.id)
    await mock_auth(user.id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist/delete",
            headers=AUTH_HEADERS,
            params={"watchlist_id": watchlist.id},
        )
    assert response.status_code == status.HTTP_200_OK
    db_watchlist = (
        (await session_test.execute(select(Watchlists).where(Watchlists.id == watchlist.id))).scalars().one_or_none()
    )
    assert db_watchlist is None