pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]
import json
from datetime import datetime

import pytest

from backend_amirainvest_com.controllers.bookmarks import get_all_user_bookmarks
from common_amirainvest_com.utils.test.factories.schema import BookmarksFactory, PostsFactory, UsersFactory
from .config import AUTH_HEADERS, client


@pytest.mark.asyncio
async def test_not_authenticated_get_bookmarks():
    response = client.get("/bookmarks/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_all_user_bookmarks():
    post_bookmarker = await UsersFactory()
    post_creator = await UsersFactory()
    post = await PostsFactory(creator_id=post_creator.id)
    bookmark = await BookmarksFactory(user_id=post_bookmarker.id, post_id=post.id)
    response = client.get("/bookmarks/", params={"user_id": bookmark.user_id}, headers=AUTH_HEADERS)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_bookmark():
    post_bookmarker = await UsersFactory()
    post_creator = await UsersFactory()
    post = await PostsFactory(creator_id=post_creator.id)
    response = client.post(
        "/bookmarks/",
        data=json.dumps(
            {
                "user_id": post_bookmarker.id,
                "post_id": post.id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_deleted": False,
            }
        ), headers=AUTH_HEADERS
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["user_id"] == post_bookmarker.id
    assert response_data["post_id"] == post.id
    assert response_data["is_deleted"] is False


@pytest.mark.asyncio
async def test_delete_bookmark():
    post_bookmarker = await UsersFactory()
    post_creator = await UsersFactory()
    post = await PostsFactory(creator_id=post_creator.id)
    bookmark = await BookmarksFactory(user_id=post_bookmarker.id, post_id=post.id)
    response = client.delete("/bookmarks", params={"bookmark_id": bookmark.id}, headers=AUTH_HEADERS)
    assert response.status_code == 200
    user_bookmarks = await get_all_user_bookmarks(post_bookmarker.id)
    assert bookmark.id not in [x.id for x in user_bookmarks]
    assert len(user_bookmarks) == 0
