pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]

import json

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas.schema import Users
from common_amirainvest_com.utils.test.factories.schema import UsersFactory

from ...config import AUTH_HEADERS


@pytest.mark.asyncio
async def test_not_authenticated():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/user/create")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get():
    user = await UsersFactory()
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/user/get", params={"user_id": user.id}, headers=AUTH_HEADERS)
        response_data = response.json()
        print(response_data)


@pytest.mark.asyncio
async def test_update(async_session_maker_test):
    session_test: AsyncSession = async_session_maker_test()
    sub_data = "fake"
    user = await UsersFactory()
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/user/update",
            headers=AUTH_HEADERS,
            params={"user_id": str(user.id)},
            data=json.dumps(
                {"is_deleted": True, "name": "Test Name 2", "username": "Test Username 2", "sub": sub_data}
            ),
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        data = (await session_test.execute(select(Users).where(Users.id == user.id))).scalars().first()

        assert response_data["is_deleted"] is True
        assert data.is_deleted is True

        assert response_data["name"] == "Test Name 2"
        assert data.name == "Test Name 2"

        assert response_data["username"] == "Test Username"
        assert data.username == "Test Username"

        assert response_data["sub"] != sub_data
        assert data.sub != sub_data


@pytest.mark.asyncio
async def test_create(async_session_maker_test, monkeypatch):
    from backend_amirainvest_com.utils import auth0_utils

    async def update_user_app_metadata_mock(*args, **kwargs):
        return

    monkeypatch.setattr(auth0_utils, "update_user_app_metadata", update_user_app_metadata_mock)

    session_test: AsyncSession = async_session_maker_test()

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/user/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "name": "test_name test_last_name",
                    "username": "test_username",
                    "email": "test@gmail.com",
                }
            ),
        )

    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED

    user_id = response_data["id"]
    assert (await session_test.execute(select(Users).where(Users.id == user_id))).one()


@pytest.mark.asyncio
async def test_create_multiple(async_session_maker_test, monkeypatch: pytest.MonkeyPatch):
    from backend_amirainvest_com.utils import auth0_utils

    async def update_user_app_metadata_mock(*args, **kwargs):
        return

    monkeypatch.setattr(auth0_utils, "update_user_app_metadata", update_user_app_metadata_mock)

    session_test: AsyncSession = async_session_maker_test()

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response_1 = await async_client.post(
            "/user/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "name": "test_name test_last_name",
                    "username": "test_username",
                    "email": "test@gmail.com",
                }
            ),  # type: ignore
        )

        response_2 = await async_client.post(
            "/user/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "name": "test_name test_last_name",
                    "username": "test_username",
                    "email": "test@gmail.com",
                }
            ),  # type: ignore
        )

    assert response_1.status_code == status.HTTP_201_CREATED
    assert response_2.status_code == status.HTTP_201_CREATED

    response_1_data = response_1.json()
    user_id_1 = response_1_data["id"]

    response_2_data = response_2.json()
    user_id_2 = response_2_data["id"]

    assert user_id_1 == user_id_2
    assert (await session_test.execute(select(Users).where(Users.id == user_id_2))).one()


@pytest.mark.asyncio
async def test_create_multiple_missmatch_email(monkeypatch):
    from backend_amirainvest_com.utils import auth0_utils

    async def update_user_app_metadata_mock(*args, **kwargs):
        return

    monkeypatch.setattr(auth0_utils, "update_user_app_metadata", update_user_app_metadata_mock)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response_1 = await async_client.post(
            "/user/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "name": "test_name test_last_name",
                    "username": "test_username",
                    "email": "test@gmail.com",
                }
            ),
        )

        response_2 = await async_client.post(
            "/user/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "name": "test_name test_last_name",
                    "username": "test_username",
                    "email": "test_bad@gmail.com",
                }
            ),
        )

    assert response_1.status_code == status.HTTP_201_CREATED
    assert response_2.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete(async_session_maker_test, monkeypatch):
    from backend_amirainvest_com.utils import auth0_utils

    async def update_user_app_metadata_mock(*args, **kwargs):
        return

    monkeypatch.setattr(auth0_utils, "update_user_app_metadata", update_user_app_metadata_mock)

    session_test: AsyncSession = async_session_maker_test()

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response_1 = await async_client.post(
            "/user/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "name": "test_name test_last_name",
                    "username": "test_username",
                    "email": "test@gmail.com",
                }
            ),
        )
        await async_client.post(
            "/user/delete",
            headers=AUTH_HEADERS,
            params={"user_id": response_1.json()["id"]},
        )

    assert len((await session_test.execute(select(Users))).all()) == 0
