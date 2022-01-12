pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]
import json
from datetime import datetime
from random import randint

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas.schema import Bookmarks, Users
from common_amirainvest_com.utils.test.factories.schema import BookmarksFactory, PostsFactory, UsersFactory

from ...config import AUTH_HEADERS


@pytest.mark.asyncio
async def test_auth():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/bookmark/list")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_list():
    post_bookmarker = await UsersFactory()
    post_creator = await UsersFactory()
    post = await PostsFactory(creator_id=post_creator.id)
    bookmark = await BookmarksFactory(user_id=post_bookmarker.id, post_id=post.id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/bookmark/list", params={"user_id": bookmark.user_id}, headers=AUTH_HEADERS)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    results = response_data["results"]
    assert type(results) == list
    assert results[0]["user_id"] == str(post_bookmarker.id)
    assert results[0]["post_id"] == post.id
    assert results[0]["is_deleted"] is False


@pytest.mark.asyncio
async def test_create(async_session_maker_test):
    session_test: AsyncSession = async_session_maker_test()

    post_bookmarker = await UsersFactory()
    post_creator = await UsersFactory()
    post = await PostsFactory(creator_id=post_creator.id, id=randint(0, 10000))

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/bookmark/create",
            params={"user_id": post_bookmarker.id},
            data=json.dumps(
                {
                    "post_id": post.id,
                    "created_at": str(datetime.utcnow()),
                    "updated_at": str(datetime.utcnow()),
                    "is_deleted": False,
                }
            ),
            headers=AUTH_HEADERS,
        )
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["user_id"] == str(post_bookmarker.id)
        assert response_data["post_id"] == post.id
        assert response_data["is_deleted"] is False
        users = await session_test.execute(select(Users).where(Users.id == post_bookmarker.id))
        users = users.scalars().all()
        assert post_bookmarker.id in [x.id for x in users]


@pytest.mark.asyncio
async def test_delete(async_session_maker_test):
    session_test: AsyncSession = async_session_maker_test()

    post_bookmarker = await UsersFactory()
    post_creator = await UsersFactory()
    post = await PostsFactory(creator_id=post_creator.id)
    bookmark = await BookmarksFactory(user_id=post_bookmarker.id, post_id=post.id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/bookmark/delete",
            params={"user_id": post_bookmarker.id, "bookmark_id": bookmark.id},
            headers=AUTH_HEADERS,
        )

    assert response.status_code == status.HTTP_200_OK

    user_bookmarks = await session_test.execute(select(Bookmarks).where(Bookmarks.user_id == post_bookmarker.id))
    assert bookmark.id not in [x.id for x in user_bookmarks]
    assert len(list(user_bookmarks)) == 0
