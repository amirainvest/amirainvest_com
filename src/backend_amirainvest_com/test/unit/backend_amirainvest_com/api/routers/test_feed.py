pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]

import pytest
from httpx import AsyncClient

from backend_amirainvest_com.api.app import app


@pytest.mark.asyncio
async def test_not_authenticated_get_feed():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/feed/subscriber/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}
