from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import Posts


pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]

import json

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.utils.test.factories.schema import PostsFactory, UsersFactory

from ...config import AUTH_HEADERS


@pytest.mark.asyncio
async def test_not_authenticated():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        post_creator = await UsersFactory()
        response = await async_client.post(
            "/post/create",
            data=json.dumps(
                {
                    "platform": "amira",
                    "platform_user_id": "test",
                    "platform_post_id": "test",
                    "profile_img_url": "test",
                    "text": "test",
                    "html": "test",
                    "title": "test",
                    "profile_url": "test",
                }
            ),
            params={"user_id": post_creator.id},
        )
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_create():
    post_creator = await UsersFactory()
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/post/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "platform": "amira",
                    "platform_user_id": "test",
                    "platform_post_id": "test",
                    "profile_img_url": "test",
                    "text": "test",
                    "html": "test",
                    "title": "test",
                    "profile_url": "test",
                }
            ),
            params={"user_id": post_creator.id},
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update(async_session_maker_test):
    session_test: AsyncSession = async_session_maker_test()

    post_creator = await UsersFactory()
    post = await PostsFactory(creator_id=post_creator.id, platform="amira")

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/post/update",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "id": post.id,
                    "platform": "amira",
                    "platform_user_id": "updated",
                    "platform_post_id": "updated",
                    "profile_img_url": "updated",
                    "text": "updated",
                    "html": "updated",
                    "title": "updated",
                    "profile_url": "updated",
                }
            ),
            params={"user_id": post_creator.id},
        )
    assert response.status_code == 200

    db_result = (await session_test.execute(select(Posts))).scalars().one()

    assert db_result.platform_user_id == "updated"
