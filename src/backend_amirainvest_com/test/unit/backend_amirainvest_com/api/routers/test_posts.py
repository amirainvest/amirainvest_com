pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]

import json
from datetime import datetime

import pytest
from httpx import AsyncClient

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.utils.test.factories.schema import PostsFactory, UsersFactory

from .config import AUTH_HEADERS


@pytest.mark.asyncio
async def test_not_authenticated_get_post():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        post_creator = await UsersFactory()
        response = await async_client.post(
            "/amira_posts/",
            data=json.dumps(
                {
                    "creator_id": str(post_creator.id),
                    "platform": "amira",
                    "platform_user_id": "test",
                    "platform_post_id": "test",
                    "profile_img_url": "test",
                    "text": "test",
                    "html": "test",
                    "title": "test",
                    "profile_url": "test",
                    "created_at": str(datetime.utcnow()),
                    "updated_at": str(datetime.utcnow()),
                }
            ),
        )
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_create_amira_post():
    post_creator = await UsersFactory()
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/amira_posts/",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "creator_id": str(post_creator.id),
                    "platform": "amira",
                    "platform_user_id": "test",
                    "platform_post_id": "test",
                    "profile_img_url": "test",
                    "text": "test",
                    "html": "test",
                    "title": "test",
                    "profile_url": "test",
                    "created_at": str(datetime.utcnow()),
                    "updated_at": str(datetime.utcnow()),
                }
            ),
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_post():
    post_creator = await UsersFactory()
    post = await PostsFactory(creator_id=post_creator.id, platform="amira")
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.put(
            "/amira_posts/",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "id": post.id,
                    "creator_id": str(post_creator.id),
                    "platform": "amira",
                    "platform_user_id": "updated",
                    "platform_post_id": "updated",
                    "profile_img_url": "updated",
                    "text": "updated",
                    "html": "updated",
                    "title": "updated",
                    "profile_url": "updated",
                    "created_at": str(datetime.utcnow()),
                    "updated_at": str(datetime.utcnow()),
                }
            ),
        )
    assert response.status_code == 200
