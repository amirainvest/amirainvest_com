import json

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.app import app
from backend_amirainvest_com.api.backend.post_route.controller import get_redis_feed, PAGE_SIZE
from backend_amirainvest_com.api.backend.post_route.model import FeedType
from common_amirainvest_com.schemas.schema import Posts, PostsModel
from common_amirainvest_com.utils.test.factories.redis_factories import posts_redis_factory
from common_amirainvest_com.utils.test.factories.schema import PostsFactory, UsersFactory, UserSubscriptionsFactory

from ...config import AUTH_HEADERS


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


async def test_create(async_session_maker_test):
    session_test: AsyncSession = async_session_maker_test()

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
    result = response.json()

    assert result["text"] == "test"

    db_result = (await session_test.execute(select(Posts))).scalars().one()

    assert db_result.platform_user_id == "test"


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
    result = response.json()

    assert result["platform_user_id"] == "updated"

    db_result = (await session_test.execute(select(Posts))).scalars().one()

    assert db_result.platform_user_id == "updated"


async def test_list_subscriber_feed(mock_auth):
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    await UserSubscriptionsFactory(subscriber_id=subscriber.id, creator_id=creator.id, is_deleted=False)

    await mock_auth(subscriber.id)

    for _ in range(0, PAGE_SIZE):
        post = await PostsFactory(creator_id=creator.id)
        posts_redis_factory(subscriber.id, FeedType.subscriber.value, PostsModel(**post.__dict__))

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/post/list",
            headers=AUTH_HEADERS,
            data=json.dumps({"feed_type": FeedType.subscriber.value}),
        )

    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert type(response_data) == dict
    assert type(response_data["posts"]) == list

    assert response_data["feed_type"] == FeedType.subscriber.value
    assert len(response_data["posts"]) == PAGE_SIZE
    assert all([response["creator_id"] == str(creator.id) for response in response_data["posts"]])


async def test_list_subscriber_feed_no_cache(mock_auth):
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    await UserSubscriptionsFactory(subscriber_id=subscriber.id, creator_id=creator.id, is_deleted=False)

    await mock_auth(subscriber.id)

    for _ in range(0, PAGE_SIZE):
        await PostsFactory(creator_id=creator.id)

    redis_feed = get_redis_feed(str(subscriber.id), FeedType.subscriber, 0, PAGE_SIZE)
    assert len(redis_feed) == 0

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/post/list",
            headers=AUTH_HEADERS,
            data=json.dumps({"feed_type": FeedType.subscriber.value}),
        )

    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert type(response_data) == dict
    assert type(response_data["posts"]) == list

    assert response_data["feed_type"] == FeedType.subscriber.value
    assert len(response_data["posts"]) == PAGE_SIZE
    assert all([response["creator_id"] == str(creator.id) for response in response_data["posts"]])

    redis_feed = get_redis_feed(str(subscriber.id), FeedType.subscriber, 0, PAGE_SIZE)
    assert len(redis_feed) == PAGE_SIZE


async def test_list_empty_subscriber_feed(mock_auth):
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    await UserSubscriptionsFactory(subscriber_id=subscriber.id, creator_id=creator.id, is_deleted=False)

    await mock_auth(subscriber.id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/post/list",
            headers=AUTH_HEADERS,
            data=json.dumps({"feed_type": FeedType.subscriber.value}),
        )

    response_data = response.json()
    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list
    assert len(response_data["posts"]) == 0
    assert response_data["feed_type"] == FeedType.discovery.value


async def test_get_creator_feed():
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    await UserSubscriptionsFactory(creator_id=creator.id, subscriber_id=subscriber.id)

    for _ in range(0, PAGE_SIZE):
        post = await PostsFactory(creator_id=creator.id)
        posts_redis_factory(str(creator.id), FeedType.creator.value, PostsModel.parse_obj(post.dict()))

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/post/list",
            headers=AUTH_HEADERS,
            data=json.dumps({"feed_type": FeedType.creator.value, "creator_id": str(creator.id)}),
        )

    response_data = response.json()
    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list
    assert response_data["feed_type"] == FeedType.creator.value

    assert len(response_data["posts"]) == PAGE_SIZE
    assert all([response["creator_id"] == str(creator.id) for response in response_data["posts"]])


async def test_get_empty_creator_feed():
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    await UserSubscriptionsFactory(creator_id=creator.id, subscriber_id=subscriber.id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/feed/creator", headers=AUTH_HEADERS, params={"creator_id": creator.id})
    response_data = response.json()
    assert response.status_code == 200
    assert type(response_data) == dict
    assert type(response_data["posts"]) == list
    assert response_data["feed_type"] == FeedType.discovery.value
    assert len(response_data["posts"]) == 0
    assert all([response["creator_id"] == str(creator.id) for response in response_data["posts"]])


@pytest.mark.parametrize("number_of_posts", [0, 10])
async def test_get_discovery_feed(number_of_posts: int):
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    await UserSubscriptionsFactory(creator_id=creator.id, subscriber_id=subscriber.id)
    for _ in range(0, number_of_posts):
        post = await PostsFactory(creator_id=creator.id)
        posts_redis_factory(creator.id, FeedType.discovery.value, PostsModel(**post.__dict__))
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/feed/discovery", headers=AUTH_HEADERS, params={"user_id": subscriber.id})
    response_data = response.json()
    assert response.status_code == 200
    assert type(response_data) == dict
    assert type(response_data["posts"]) == list
    assert response_data["feed_type"] == FeedType.discovery.value
    assert len(response_data["posts"]) == number_of_posts
    assert all([response["creator_id"] == str(creator.id) for response in response_data["posts"]])
