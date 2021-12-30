import json


pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]

import pytest
from httpx import AsyncClient

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.utils.test.factories.schema import UsersFactory
from common_amirainvest_com.schemas.schema import Users
from sqlalchemy import select
from .config import AUTH_HEADERS


@pytest.mark.asyncio
async def test_not_authenticated_get_user():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/user/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_user():
    user = await UsersFactory()
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/user/", params={"user_id": user.id}, headers=AUTH_HEADERS)
        response_data = response.json()


@pytest.mark.asyncio
async def test_update_user(session_test):
    user = await UsersFactory()
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.put(
            "/user/",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "id": str(user.id),
                    "is_deleted": True,
                    "name": "Test Name 2",
                    "username": "Test Username 2"
                }
            )
        )
        assert response.status_code == 200
        response_data = response.json()
        data = (await session_test.execute(select(Users))).scalars().all()
        assert response_data["is_deleted"] is True
        assert data[0].is_deleted is True
        assert response_data["name"] == "Test Name 2"
        assert data[0].name == "Test Name 2"
        assert response_data["username"] == "Test Username 2"
        assert data[0].username == "Test Username 2"


@pytest.mark.asyncio
async def test_create_user(session_test):
    user = await UsersFactory()
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/user/", params={"user_id": user.id}, headers=AUTH_HEADERS)
        response_data = response.json()
        data = (await session_test.execute(select(Users))).scalars().all()
