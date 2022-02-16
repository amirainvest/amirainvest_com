import json

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas.schema import Posts

from ...config import AUTH_HEADERS


async def test_get(factory):
    post = await factory.gen("posts")
    post2 = await factory.gen("posts")
    await factory.gen("posts")

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/post/get",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "ids": [
                        post["posts"].id,
                        post2["posts"].id,
                    ],
                }
            ),
        )

    assert response.status_code == 200
    result = response.json()

    assert len(result) == 2
    assert result[0]["id"] == post["posts"].id


async def test_create(async_session_maker_test, factory, mock_auth):
    session_test: AsyncSession = async_session_maker_test()
    user = await factory.gen("users")
    user_id = user["users"].id
    await mock_auth(user_id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/post/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "title": "",
                    "content": "test",
                    "photos": [],
                    "subscription_level": "standard",
                    "platform": "twitter",
                    "creator_id": user_id,
                    "platform_display_name": "",
                    "platform_user_id": "test",
                    "platform_img_url": "",
                    "platform_profile_url": "",
                    "twitter_handle": "",
                    "platform_post_id": "",
                    "platform_post_url": "",
                }
            ),
        )
    assert response.status_code == 200
    result = response.json()

    assert result["content"] == "test"

    db_result = (await session_test.execute(select(Posts))).scalars().one()

    assert db_result.platform_user_id == "test"


async def test_update(async_session_maker_test, factory, mock_auth):
    session_test: AsyncSession = async_session_maker_test()

    post = await factory.gen("posts")
    creator_id = post["users"].id
    await mock_auth(creator_id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/post/update",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "id": post["posts"].id,
                    "creator_id": creator_id,
                    "subscription_level": "standard",
                    "title": "",
                    "content": "",
                    "photos": [],
                    "platform": "twitter",
                    "platform_display_name": "",
                    "platform_user_id": "updated",
                    "platform_img_url": "",
                    "platform_profile_url": "",
                    "twitter_handle": "",
                    "platform_post_id": "",
                    "platform_post_url": "",
                }
            ),
        )
    assert response.status_code == 200
    result = response.json()

    assert result["platform_user_id"] == "updated"

    db_result = (await session_test.execute(select(Posts))).scalars().one()

    assert db_result.platform_user_id == "updated"
