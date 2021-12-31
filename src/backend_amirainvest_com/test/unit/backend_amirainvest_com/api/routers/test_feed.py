pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]

from random import randint

import pytest
from httpx import AsyncClient

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas.schema import PostsModel
from common_amirainvest_com.utils.test.factories.redis_factories import posts_redis_factory
from common_amirainvest_com.utils.test.factories.schema import PostsFactory, UsersFactory, UserSubscriptionsFactory

from .config import AUTH_HEADERS


@pytest.mark.asyncio
async def test_get_subscriber_feed():
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    await UserSubscriptionsFactory(subscriber_id=subscriber.id, creator_id=creator.id, is_deleted=False)

    for _ in range(0, 3):
        post = await PostsFactory(creator_id=creator.id, id=randint(0, 10000))
        posts_redis_factory(creator.id, "subscriber", PostsModel(**{k: v for k, v in post.__dict__.items()}))

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get(
            "/feed/subscriber/", headers=AUTH_HEADERS, params={"subscriber_id": subscriber.id}
        )

    response_data = response.json()

    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list

    assert response_data["feed_type"] == "subscriber"

    assert len(response_data["posts"]) == 3
    assert all([response["creator_id"] == str(creator.id) for response in response_data["posts"]])


@pytest.mark.asyncio
async def test_get_empty_subscriber_feed():
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    await UserSubscriptionsFactory(subscriber_id=subscriber.id, creator_id=creator.id, is_deleted=False)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get(
            "/feed/subscriber/", headers=AUTH_HEADERS, params={"subscriber_id": subscriber.id}
        )

    response_data = response.json()

    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list

    assert response_data["feed_type"] == "discovery"

    assert len(response_data["posts"]) == 0
    assert all([response["creator_id"] == str(creator.id) for response in response_data["posts"]])


@pytest.mark.asyncio
async def test_get_creator_feed():
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    await UserSubscriptionsFactory(creator_id=creator.id, subscriber_id=subscriber.id)

    for _ in range(0, 3):
        post = await PostsFactory(creator_id=creator.id, id=randint(0, 10000))
        post_model = PostsModel(**{k: v for k, v in post.__dict__.items()})
        posts_redis_factory(creator.id, "creator", post_model)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/feed/creator/", headers=AUTH_HEADERS, params={"creator_id": creator.id})

    response_data = response.json()

    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list

    assert response_data["feed_type"] == "creator"

    assert len(response_data["posts"]) == 3
    assert all([response["creator_id"] == str(creator.id) for response in response_data["posts"]])


@pytest.mark.asyncio
async def test_get_empty_creator_feed():
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    await UserSubscriptionsFactory(creator_id=creator.id, subscriber_id=subscriber.id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/feed/creator/", headers=AUTH_HEADERS, params={"creator_id": creator.id})

    response_data = response.json()

    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list

    assert response_data["feed_type"] == "discovery"

    assert len(response_data["posts"]) == 0
    assert all([response["creator_id"] == str(creator.id) for response in response_data["posts"]])


@pytest.mark.asyncio
@pytest.mark.parametrize("number_of_posts", [0, 10])
async def test_get_discovery_feed(number_of_posts: int):
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    await UserSubscriptionsFactory(creator_id=creator.id, subscriber_id=subscriber.id)

    for _ in range(0, number_of_posts):
        post = await PostsFactory(creator_id=creator.id, id=randint(0, 10000))
        post_model = PostsModel(**{k: v for k, v in post.__dict__.items()})
        posts_redis_factory(creator.id, "discovery", post_model)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/feed/discovery/", headers=AUTH_HEADERS, params={"user_id": subscriber.id})

    response_data = response.json()

    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list

    assert response_data["feed_type"] == "discovery"

    assert len(response_data["posts"]) == number_of_posts
    assert all([response["creator_id"] == str(creator.id) for response in response_data["posts"]])
