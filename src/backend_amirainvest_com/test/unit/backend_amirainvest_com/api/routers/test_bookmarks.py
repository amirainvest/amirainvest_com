pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]
import json
from datetime import datetime
from random import randint

import pytest
from httpx import AsyncClient

from backend_amirainvest_com.api.app import app
from backend_amirainvest_com.controllers.bookmarks import get_all_user_bookmarks
from common_amirainvest_com.utils.test.factories.schema import BookmarksFactory, PostsFactory, UsersFactory
from .config import AUTH_HEADERS


@pytest.mark.asyncio
async def test_not_authenticated_get_bookmarks():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/bookmarks/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_all_user_bookmarks(session_test):
    post_bookmarker = await UsersFactory()
    post_creator = await UsersFactory()
    post = await PostsFactory(creator_id=post_creator.id)
    bookmark = await BookmarksFactory(user_id=post_bookmarker.id, post_id=post.id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/bookmarks/", params={"user_id": bookmark.user_id}, headers=AUTH_HEADERS)
    response_data = response.json()
    assert type(response_data) == list
    assert response_data[0]["user_id"] == str(post_bookmarker.id)
    assert response_data[0]["post_id"] == post.id
    assert response_data[0]["is_deleted"] is False
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_bookmark():
    post_bookmarker = await UsersFactory()
    post_creator = await UsersFactory()
    post = await PostsFactory(creator_id=post_creator.id, id=randint(0, 10000))
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/bookmarks/",
            data=json.dumps(
                {
                    "user_id": str(post_bookmarker.id),
                    "post_id": post.id,
                    "created_at": str(datetime.utcnow()),
                    "updated_at": str(datetime.utcnow()),
                    "is_deleted": False,
                }
            ), headers=AUTH_HEADERS
        )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["user_id"] == str(post_bookmarker.id)
    assert response_data["post_id"] == post.id
    assert response_data["is_deleted"] is False


@pytest.mark.asyncio
async def test_delete_bookmark():
    post_bookmarker = await UsersFactory()
    post_creator = await UsersFactory()
    post = await PostsFactory(creator_id=post_creator.id)
    bookmark = await BookmarksFactory(user_id=post_bookmarker.id, post_id=post.id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.delete("/bookmarks/", params={"bookmark_id": bookmark.id}, headers=AUTH_HEADERS)
    assert response.status_code == 200
    user_bookmarks = await get_all_user_bookmarks(post_bookmarker.id)
    assert bookmark.id not in [x.id for x in user_bookmarks]
    assert len(user_bookmarks) == 0
