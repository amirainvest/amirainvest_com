pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]

import pytest
from httpx import AsyncClient
from sqlalchemy.future import select

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas.schema import BroadcastRequests
from common_amirainvest_com.utils.test.factories.schema import BroadcastRequestsFactory, UsersFactory

from .config import AUTH_HEADERS


@pytest.mark.asyncio
async def test_not_authenticated_get_broadcast_requests():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/broadcast_requests")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_broadcast_requests_for_creator():
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    broadcast_request = await BroadcastRequestsFactory(subscriber_id=subscriber.id, creator_id=creator.id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get(
            "/broadcast_requests", params={"creator_id": str(creator.id)}, headers=AUTH_HEADERS
        )
    assert response.status_code == 200
    response_data = response.json()
    assert type(response_data) == list
    assert broadcast_request.id in [x["id"] for x in response_data]
    response_broadcast_request = response_data[0]
    assert str(response_broadcast_request["creator_id"]) == str(creator.id)
    assert str(response_broadcast_request["subscriber_id"]) == str(subscriber.id)


@pytest.mark.asyncio
async def test_create_broadcast_request(session_test):
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/broadcast_requests",
            params={
                "requester_id": str(subscriber.id),
                "creator_id": str(creator.id),
            },
            headers=AUTH_HEADERS,
        )
    assert response.status_code == 200
    response_data = response.json()
    assert type(response_data) == dict
    assert str(response_data["creator_id"]) == str(creator.id)
    assert str(response_data["subscriber_id"]) == str(subscriber.id)
    broadcast_request_data = await session_test.execute(
        select(BroadcastRequests).where(BroadcastRequests.creator_id == response_data["creator_id"])
    )
    broadcast_request_data = broadcast_request_data.scalars().all()
    assert str(broadcast_request_data[0].creator_id) == str(creator.id)
    assert str(broadcast_request_data[0].subscriber_id) == str(subscriber.id)
