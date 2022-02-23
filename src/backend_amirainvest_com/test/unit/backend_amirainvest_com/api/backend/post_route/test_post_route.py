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


async def test_list(factory):
    await factory.gen("posts", {"posts": {"content": "search_result_1"}})
    await factory.gen("posts", {"posts": {"content": "search_result_2"}})

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        list_response = await async_client.post(
            "/post/list",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "filters": [
                        {
                            "attribute": "content",
                            "filter_type": "substring_match",
                            "value": "search_result_1",
                        }
                    ]
                }
            ),
        )

    list_response_json = list_response.json()
    assert list_response_json["result_count"] == 1
    assert len(list_response_json["results"]) == 1

    post_result = list_response_json["results"][0]
    assert post_result["content"] == "search_result_1"


async def test_list_multiple_matches(factory):
    await factory.gen("posts", {"posts": {"content": "search_result_1"}})
    await factory.gen("posts", {"posts": {"content": "search_result_2"}})
    await factory.gen("posts", {"posts": {"content": "wont_show_up"}})

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        list_response = await async_client.post(
            "/post/list",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "filters": [
                        {
                            "attribute": "content",
                            "filter_type": "substring_match",
                            "value": "arch_resu",
                        }
                    ]
                }
            ),
        )

    list_response_json = list_response.json()
    assert list_response_json["result_count"] == 2
    assert len(list_response_json["results"]) == 2
