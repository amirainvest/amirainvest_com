import json


pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]

import pytest
from httpx import AsyncClient

from backend_amirainvest_com.api.app import app
from .config import AUTH_HEADERS
from datetime import datetime
from common_amirainvest_com.utils.test.factories.schema import HuskRequestsFactory


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
async def test_create_husk_request():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/husk_requests/", headers=AUTH_HEADERS, data=json.dumps(
                {
                    "twitter_user_id": "Test",
                    "youtube_channel_id": "Test",
                    "substack_username": "Test",
                    "created_at": str(datetime.utcnow()),
                    "fulfilled": False
                }
            )
        )
    print(response.text)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_delete_husk_request():
    husk_request = await HuskRequestsFactory()
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.delete("/husk_requests/", headers=AUTH_HEADERS, params={
            "husk_request_id": husk_request.id
        })
    assert response.status_code == 200
