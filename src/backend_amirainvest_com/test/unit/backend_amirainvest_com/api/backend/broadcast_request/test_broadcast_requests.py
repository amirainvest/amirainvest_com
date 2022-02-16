from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas.schema import BroadcastRequests

from ...config import AUTH_HEADERS


async def test_auth():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/broadcast_request/list")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Not authenticated"}


async def test_list(factory):
    broadcast_request = await factory.gen("broadcast_requests")
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/broadcast_request/list",
            params={"creator_id": str(broadcast_request["broadcast_requests"].creator_id)},
            headers=AUTH_HEADERS,
        )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    results = response_data["results"]
    assert type(results) == list
    assert broadcast_request["broadcast_requests"].id in [x["id"] for x in results]
    response_broadcast_request = results[0]
    assert str(response_broadcast_request["creator_id"]) == str(broadcast_request["broadcast_requests"].creator_id)
    assert str(response_broadcast_request["subscriber_id"]) == str(
        broadcast_request["broadcast_requests"].subscriber_id
    )


async def test_create(async_session_maker_test, factory, mock_auth):
    session_test: AsyncSession = async_session_maker_test()

    creator = await factory.gen("users")
    subscriber = await factory.gen("users")
    await mock_auth(subscriber["users"].id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/broadcast_request/create",
            params={
                "creator_id": str(creator["users"].id),
            },
            headers=AUTH_HEADERS,
        )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert type(response_data) == dict
    assert str(response_data["creator_id"]) == str(creator["users"].id)
    assert str(response_data["subscriber_id"]) == str(subscriber["users"].id)

    broadcast_request_data = await session_test.execute(
        select(BroadcastRequests).where(BroadcastRequests.creator_id == response_data["creator_id"])
    )
    broadcast_request_data = broadcast_request_data.scalars().all()

    assert str(broadcast_request_data[0].creator_id) == str(creator["users"].id)
    assert str(broadcast_request_data[0].subscriber_id) == str(subscriber["users"].id)
