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


# @pytest.mark.asyncio
# async def test_update_user(session_test):
#     user = await UsersFactory()
#     async with AsyncClient(app=app, base_url="http://test") as async_client:
#         response = await async_client.put(
#             "/user/",
#             headers=AUTH_HEADERS,
#             data=json.dumps(
#                 {
#                     "id": str(user.id),
#                     "is_deleted": True,
#                     "name": "Test Name 2",
#                     "username": "Test Username 2"
#                 }
#             )
#         )
#         assert response.status_code == 200
#         response_data = response.json()
#         data = (await session_test.execute(select(Users))).scalars().all()
#         assert response_data["is_deleted"] is True
#         assert data[0].is_deleted is True
#         assert response_data["name"] == "Test Name 2"
#         assert data[0].name == "Test Name 2"
#         assert response_data["username"] == "Test Username 2"
#         assert data[0].username == "Test Username 2"


@pytest.mark.asyncio
async def test_create_user(session_test):
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/user/", data=json.dumps(
                {
                    "sub": "Test Sub",
                    "name": "Test Name",
                    "username": "Test Username",
                    "picture_url": "photo@test.com",
                    "email": "test@test.com",
                }
            ), headers=AUTH_HEADERS
        )
        response_data = response.json()
        assert response_data["sub"] == "Test Sub"
        assert response_data["name"] == "Test Name"
        assert response_data["username"] == "Test Username"
        assert response_data["picture_url"] == "photo@test.com"
        assert response_data["email"] == "test@test.com"
        data = (await session_test.execute(select(Users))).scalars().first()
        assert data.sub == "Test Sub"
        assert data.name == "Test Name"
        assert data.username == "Test Username"
        assert data.picture_url == "photo@test.com"
        assert data.email == "test@test.com"


@pytest.mark.asyncio
async def test_is_existing(session_test):
    user = await UsersFactory()
    non_existing_user_id = "054d6d6f-2e99-4699-b433-1309ea6fac99"
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get(
            "/user/is_existing/", headers=AUTH_HEADERS, params={
                "user_id": user.id
            }
        )
        response_data = response.json()
        data = (await session_test.execute(select(Users).where(Users.id == user.id))).scalars().first()
        assert data
        assert data.id == user.id
        assert response_data is True
        response = await async_client.get(
            "/user/is_existing/", headers=AUTH_HEADERS, params={"user_id": non_existing_user_id}
        )
        response_data = response.json()
        assert response_data is False
        data = (await session_test.execute(select(Users).where(Users.id == non_existing_user_id))).scalars().first()
        assert not data


# @pytest.mark.asyncio
# async def test_deactivate_user(session_test):
#     user = await UsersFactory()
#     async with AsyncClient(app=app, base_url="http://test") as async_client:
#         response = await async_client.put(
#             "/user/deactivate/", params={"user_id": user.id}, headers=AUTH_HEADERS
#         )
#         response_data = response.json()
#         print(response_data)
#         assert response_data["is_deactivated"] is True
#         data = (await session_test.execute(select(Users))).scalars().first()
#         print("123134", data.__dict__)
#         assert data
#         assert data.is_deactivated is True
#
#
# @pytest.mark.asyncio
# async def test_reactivate_user(session_test):
#     user = await UsersFactory(is_deactivated=True)
#     async with AsyncClient(app=app, base_url="http://test") as async_client:
#         response = await async_client.put(
#             "/user/reactivate/", params={"user_id": user.id}, headers=AUTH_HEADERS
#         )
#         response_data = response.json()
#         assert response_data["is_deactivated"] is False
#         data = (await session_test.execute(select(Users))).scalars().first()
#         assert data
#         assert data.is_deactivated is False
#
#
# @pytest.mark.asyncio
# async def test_delete_user(session_test):
#     user = await UsersFactory()
#     async with AsyncClient(app=app, base_url="http://test") as async_client:
#         response = await async_client.put(
#             "/user/delete/", params={"user_id": user.id}, headers=AUTH_HEADERS
#         )
#         response_data = response.json()
#         assert response_data["is_deleted"] is True
#         data = (await session_test.execute(select(Users))).scalars().first()
#         assert data
#         assert data.is_deleted is True
#
#
# @pytest.mark.asyncio
# async def test_undelete_user(session_test):
#     user = await UsersFactory(is_deleted=True)
#     async with AsyncClient(app=app, base_url="http://test") as async_client:
#         response = await async_client.put(
#             "/user/undelete/", params={"user_id": user.id}, headers=AUTH_HEADERS
#         )
#         response_data = response.json()
#         assert response_data["is_deleted"] is False
#         data = (await session_test.execute(select(Users))).scalars().first()
#         assert data
#         assert data.is_deleted is False
#
#
# @pytest.mark.asyncio
# async def test_claim_user(session_test):
#     user = await UsersFactory(is_claimed=False)
#     async with AsyncClient(app=app, base_url="http://test") as async_client:
#         response = await async_client.put(
#             "/user/claim_user/", params={"user_id": user.id}, headers=AUTH_HEADERS
#         )
#         response_data = response.json()
#         assert response_data["is_claimed"] is True
#         data = (await session_test.execute(select(Users))).scalars().all()
#         assert data
