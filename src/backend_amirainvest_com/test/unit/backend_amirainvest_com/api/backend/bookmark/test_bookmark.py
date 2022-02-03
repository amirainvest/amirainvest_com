import json
from datetime import datetime

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas.schema import Bookmarks, Users

from ...config import AUTH_HEADERS


async def test_auth():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/bookmark/list")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Not authenticated"}


async def test_list(factory):

    post_bookmarker = await factory.gen("users")
    post_creator = await factory.gen("users")
    post = await factory.gen("posts", {"posts": {"creator_id": post_creator["users"].id}})
    bookmark = await factory.gen(
        "bookmarks", {"bookmarks": {"user_id": post_bookmarker["users"].id, "post_id": post["posts"].id}}
    )

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/bookmark/list", params={"user_id": bookmark["bookmarks"].user_id}, headers=AUTH_HEADERS
        )

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    results = response_data["results"]
    assert type(results) == list
    assert results[0]["user_id"] == str(post_bookmarker["users"].id)
    assert results[0]["post_id"] == post["posts"].id
    assert results[0]["is_deleted"] is False


async def test_create(async_session_maker_test, factory):
    session_test: AsyncSession = async_session_maker_test()

    post_bookmarker = await factory.gen("users")
    post_creator = await factory.gen("users")
    post = await factory.gen("posts", {"posts": {"creator_id": post_creator["users"].id}})

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/bookmark/create",
            params={"user_id": post_bookmarker["users"].id},
            data=json.dumps(
                {
                    "post_id": post["posts"].id,
                    "created_at": str(datetime.utcnow()),
                    "updated_at": str(datetime.utcnow()),
                    "is_deleted": False,
                }
            ),
            headers=AUTH_HEADERS,
        )
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["user_id"] == str(post_bookmarker["users"].id)
        assert response_data["post_id"] == post["posts"].id
        assert response_data["is_deleted"] is False
        users = await session_test.execute(select(Users).where(Users.id == post_bookmarker["users"].id))
        users = users.scalars().all()
        assert post_bookmarker["users"].id in [x.id for x in users]


async def test_delete(async_session_maker_test, factory):
    session_test: AsyncSession = async_session_maker_test()

    post_bookmarker = await factory.gen("users")
    post_creator = await factory.gen("users")
    post = await factory.gen("posts", {"posts": {"creator_id": post_creator["users"].id}})
    bookmark = await factory.gen(
        "bookmarks", {"bookmarks": {"user_id": post_bookmarker["users"].id, "post_id": post["posts"].id}}
    )

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/bookmark/delete",
            params={"user_id": post_bookmarker["users"].id, "bookmark_id": bookmark["bookmarks"].id},
            headers=AUTH_HEADERS,
        )

    assert response.status_code == status.HTTP_200_OK

    user_bookmarks = await session_test.execute(
        select(Bookmarks).where(Bookmarks.user_id == post_bookmarker["users"].id)
    )
    assert bookmark["bookmarks"].id not in [x.id for x in user_bookmarks]
    assert len(list(user_bookmarks)) == 0


async def test_update(async_session_maker_test):
    pass
