import json

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas.schema import Users

from ...config import AUTH_HEADERS


async def test_not_authenticated():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/user/create")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Not authenticated"}


async def test_get(factory):
    user = await factory.gen("users")
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        await async_client.post("/user/get", params={"user_id": user["users"].id}, headers=AUTH_HEADERS)


async def test_update(async_session_maker_test, mock_auth, factory):
    session_test: AsyncSession = async_session_maker_test()
    sub_data = "fake"

    user = await factory.gen("users")
    user_id = user["users"].id
    await mock_auth(user_id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/user/update",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "is_deleted": True,
                    "first_name": "FirstTest",
                    "last_name": "LastTest",
                    "username": "TestUser",
                    "sub": sub_data,
                }
            ),
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        data = (await session_test.execute(select(Users).where(Users.id == user_id))).scalars().first()
        assert data is not None

        assert response_data["is_deleted"] is True
        assert data.is_deleted is True

        assert response_data["first_name"] == "FirstTest"
        assert data.first_name == "FirstTest"

        assert response_data["last_name"] == "LastTest"
        assert data.last_name == "LastTest"

        assert response_data["username"] == user["users"].username
        assert data.username == user["users"].username

        assert response_data["sub"] != sub_data
        assert data.sub != sub_data


async def test_create(async_session_maker_test, monkeypatch, factory):
    from backend_amirainvest_com.utils import auth0_utils

    async def update_user_app_metadata_mock(*args, **kwargs):
        return

    monkeypatch.setattr(auth0_utils, "update_user_app_metadata", update_user_app_metadata_mock)

    session_test: AsyncSession = async_session_maker_test()
    security = await factory.gen("securities")
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/user/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "first_name": "test_first",
                    "last_name": "test_last",
                    "username": "test_username",
                    "email": "test@gmail.com",
                    "benchmark": security["securities"].id,
                }
            ),
        )

        response_data = response.json()

        assert response.status_code == status.HTTP_201_CREATED

        user_id = response_data["id"]
        assert (await session_test.execute(select(Users).where(Users.id == user_id))).one()


async def test_create_multiple(async_session_maker_test, monkeypatch: pytest.MonkeyPatch, factory):
    from backend_amirainvest_com.utils import auth0_utils

    async def update_user_app_metadata_mock(*args, **kwargs):
        return

    monkeypatch.setattr(auth0_utils, "update_user_app_metadata", update_user_app_metadata_mock)

    session_test: AsyncSession = async_session_maker_test()
    security = await factory.gen("securities")
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response_1 = await async_client.post(
            "/user/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "first_name": "test_first",
                    "last_name": "test_last",
                    "username": "test_username",
                    "email": "test@gmail.com",
                    "benchmark": security["securities"].id,
                }
            ),  # type: ignore
        )

        response_2 = await async_client.post(
            "/user/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "first_name": "test_first",
                    "last_name": "test_last",
                    "username": "test_username",
                    "email": "test@gmail.com",
                    "benchmark": security["securities"].id,
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


async def test_create_multiple_missmatch_email(monkeypatch, factory):
    from backend_amirainvest_com.utils import auth0_utils

    async def update_user_app_metadata_mock(*args, **kwargs):
        return

    monkeypatch.setattr(auth0_utils, "update_user_app_metadata", update_user_app_metadata_mock)

    security = await factory.gen("securities")
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response_1 = await async_client.post(
            "/user/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "first_name": "test_first",
                    "last_name": "test_last",
                    "username": "test_username",
                    "email": "test@gmail.com",
                    "benchmark": security["securities"].id,
                }
            ),
        )

        response_2 = await async_client.post(
            "/user/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "first_name": "test_name",
                    "last_name": "test_last_name",
                    "username": "test_username",
                    "email": "test_bad@gmail.com",
                    "benchmark": security["securities"].id,
                }
            ),
        )

    assert response_1.status_code == status.HTTP_201_CREATED
    assert response_2.status_code == status.HTTP_409_CONFLICT


async def test_delete(async_session_maker_test, monkeypatch, factory):
    from backend_amirainvest_com.utils import auth0_utils

    async def update_user_app_metadata_mock(*args, **kwargs):
        return

    monkeypatch.setattr(auth0_utils, "update_user_app_metadata", update_user_app_metadata_mock)

    session_test: AsyncSession = async_session_maker_test()

    security = await factory.gen("securities")
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response_1 = await async_client.post(
            "/user/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "first_name": "test_first",
                    "last_name": "test_last_name",
                    "username": "test_username",
                    "email": "test@gmail.com",
                    "benchmark": security["securities"].id,
                }
            ),
        )

        await async_client.post(
            "/user/delete",
            headers=AUTH_HEADERS,
            params={"user_id": response_1.json()["id"]},
        )

    assert len((await session_test.execute(select(Users))).all()) == 0


async def test_list(factory):
    await factory.gen("users")
    await factory.gen("users")

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        list_response = await async_client.post(
            "/user/list",
            headers=AUTH_HEADERS,
            data=json.dumps({}),
        )
    list_response_json = list_response.json()

    assert list_response_json["result_count"] == 2


async def test_list_search(factory):
    await factory.gen("users", {"users": {"first_name": "searchable_first_name"}})
    await factory.gen("users", {"users": {"first_name": "NA", "username": "searchable_username"}})

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        list_response = await async_client.post(
            "/user/list",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "filters": [
                        {
                            "attribute": "first_name",
                            "filter_type": "substring_match",
                            "value": "able_first",
                        }
                    ]
                }
            ),
        )

    list_response_json = list_response.json()
    assert list_response_json["result_count"] == 1

    user_result = list_response_json["results"][0]
    assert user_result["first_name"] == "searchable_first_name"


async def test_list_search_full_name(factory):
    await factory.gen("users", {"users": {"first_name": "searchable_first_name", "last_name": "searchable_last_name"}})
    await factory.gen("users", {"users": {"first_name": "NA", "username": "searchable_username"}})

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        list_response = await async_client.post(
            "/user/list",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "filters": [
                        {
                            "attribute": "full_name",
                            "filter_type": "substring_match",
                            "value": "rchable_first_namesearchable_last_na",
                        }
                    ]
                }
            ),
        )

    list_response_json = list_response.json()
    assert list_response_json["result_count"] == 1

    user_result = list_response_json["results"][0]
    assert user_result["first_name"] == "searchable_first_name"
    assert user_result["last_name"] == "searchable_last_name"


async def test_list_search_order(factory):
    await factory.gen("users", {"users": {"first_name": "1"}})
    await factory.gen("users", {"users": {"first_name": "2"}})

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        list_response = await async_client.post(
            "/user/list",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "sort": {
                        "attribute": "first_name",
                        "order": "desc",
                    }
                }
            ),
        )

    list_response_json = list_response.json()
    assert list_response_json["result_count"] == 2

    user_result = list_response_json["results"][0]
    assert user_result["first_name"] == "2"
