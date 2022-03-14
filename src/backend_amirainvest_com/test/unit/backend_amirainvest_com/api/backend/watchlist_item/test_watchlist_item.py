import json

from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas import schema

from ...config import AUTH_HEADERS


async def test_create_watchlist_item(async_session_maker_test, mock_auth, factory):
    session_test: AsyncSession = async_session_maker_test()
    watchlist = await factory.gen("watchlists")
    securities = await factory.gen("securities")
    await mock_auth(watchlist["users"].id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_item/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "creator_id": str(watchlist["users"].id),
                    "watchlist_id": watchlist["watchlists"].id,
                    "ticker": securities["securities"].ticker_symbol,
                    "note": "This is a note",
                }
            ),
        )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data
    watchlist_items = (
        (
            await session_test.execute(
                select(schema.WatchlistItems).where(schema.WatchlistItems.watchlist_id == watchlist["watchlists"].id)
            )
        )
        .scalars()
        .all()
    )
    assert watchlist_items
    assert watchlist_items[0].ticker == securities["securities"].ticker_symbol
    assert watchlist_items[0].note == "This is a note"
    assert watchlist_items[0].watchlist_id == watchlist["watchlists"].id


async def test_delete_watchlist_item(async_session_maker_test, mock_auth, factory):
    session_test: AsyncSession = async_session_maker_test()
    watchlist_item = await factory.gen("watchlist_items")
    await mock_auth(watchlist_item["users"].id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_item/delete",
            headers=AUTH_HEADERS,
            params={"watchlist_item_id": watchlist_item["watchlist_items"].id},
        )
    assert response.status_code == status.HTTP_200_OK
    assert (
        await session_test.execute(
            select(schema.WatchlistItems).where(schema.WatchlistItems.id == watchlist_item["watchlist_items"].id)
        )
    ).scalars().all() == []


async def test_update_watchlist_item(async_session_maker_test, mock_auth, factory):
    watchlist_item = await factory.gen("watchlist_items")
    await mock_auth(watchlist_item["users"].id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/watchlist_item/update",
            headers=AUTH_HEADERS,
            params={"creator_id": watchlist_item["users"].id},
            data=json.dumps(
                {
                    "id": watchlist_item["watchlist_items"].id,
                    "note": "Updated Note",
                    "ticker": watchlist_item["watchlist_items"].ticker,
                }
            ),
        )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["note"] == "Updated Note"
    assert response_data["ticker"] == watchlist_item["watchlist_items"].ticker
    assert response_data["id"] == watchlist_item["watchlist_items"].id
