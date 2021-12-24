pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]

import pytest
from httpx import AsyncClient

from backend_amirainvest_com.api.app import app


@pytest.mark.asyncio
async def test_not_authenticated_get_husk_requests():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/husk_requests/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_husk_requests():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/husk_requests/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_husk_request():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/husk_requests/")
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_delete_husk_request():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.delete("/husk_requests/")
    assert response.status_code == 200
