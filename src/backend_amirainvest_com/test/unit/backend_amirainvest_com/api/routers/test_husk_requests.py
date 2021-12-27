import json


pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]

from datetime import datetime

import pytest
from httpx import AsyncClient

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.utils.test.factories.schema import HuskRequestsFactory
from common_amirainvest_com.schemas.schema import HuskRequests
from sqlalchemy import select

from .config import AUTH_HEADERS


@pytest.mark.asyncio
async def test_not_authenticated_get_husk_requests():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/husk_requests/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_husk_requests():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/husk_requests/", headers=AUTH_HEADERS)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_husk_request(session_test):
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/husk_requests/",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "twitter_user_id": "Test",
                    "youtube_channel_id": "Test",
                    "substack_username": "Test",
                    "created_at": str(datetime.utcnow()),
                    "fulfilled": False,
                }
            ),
        )
    assert response.status_code == 201
    response_data = response.json()
    print(response_data)
    husk_requests = await session_test.execute(select(HuskRequests).where(HuskRequests.id == response_data["id"]))
    husk_requests = husk_requests.scalars().all()
    assert husk_requests
    assert response_data["id"] in [x["id"] for x in husk_requests]


@pytest.mark.asyncio
async def test_delete_husk_request(session_test):
    husk_request = await HuskRequestsFactory()
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.delete(
            "/husk_requests/", headers=AUTH_HEADERS, params={"husk_request_id": husk_request.id}
        )
    assert response.status_code == 200
    husk_requests = await session_test.execute(select(HuskRequests).where(HuskRequests.id == husk_request.id))
    assert not husk_requests
