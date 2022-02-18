from fastapi import status
from httpx import AsyncClient

from backend_amirainvest_com.api.app import app

from ...config import AUTH_HEADERS


async def test_get(factory):
    num_users = 4
    await factory.gen("users", {"users": {"trading_strategies": ["Long/Short"], "public_profile_deactivate": True}})
    for _ in range(0, num_users):
        await factory.gen("users", {"users": {"trading_strategies": ["Long/Short"]}})
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/discovery/get",
            headers=AUTH_HEADERS,
        )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data[0]["trading_strategy"] == "Long/Short"
    assert len(response_data[0]["values"]) == num_users
