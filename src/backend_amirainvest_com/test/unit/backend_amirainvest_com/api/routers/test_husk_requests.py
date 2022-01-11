from sqlalchemy.ext.asyncio import AsyncSession


pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]
import json

import pytest
from httpx import AsyncClient
from sqlalchemy.future import select

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas.schema import HuskRequests
from common_amirainvest_com.utils.test.factories.schema import HuskRequestsFactory

from .config import AUTH_HEADERS


@pytest.mark.asyncio
async def test_get_husk_requests():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/husk_requests/", headers=AUTH_HEADERS)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_husk_request(async_session_maker_test):
    session_test: AsyncSession = async_session_maker_test()

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/husk_requests/",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "twitter_user_id": "Test",
                    "youtube_channel_id": "Test",
                    "substack_username": "Test",
                    "fulfilled": False,
                }
            ),
        )
    assert response.status_code == 201
    response_data = response.json()

    husk_requests = await session_test.execute(select(HuskRequests))
    husk_requests = husk_requests.scalars().one()

    assert response_data["id"] == husk_requests.id


@pytest.mark.asyncio
async def test_delete_husk_request(async_session_maker_test):
    session_test: AsyncSession = async_session_maker_test()

    husk_request = await HuskRequestsFactory()

    husk_requests = await session_test.execute(select(HuskRequests))
    husk_requests = husk_requests.scalars().all()
    assert len(husk_requests) == 1

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.delete(
            "/husk_requests/", headers=AUTH_HEADERS, params={"husk_request_id": husk_request.id}
        )
    assert response.status_code == 200

    husk_requests = await session_test.execute(select(HuskRequests))
    husk_requests = husk_requests.scalars().all()
    assert husk_requests == []
