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
    await UserSubscriptionsFactory(
        subscriber_id=subscriber.id,
        creator_id=creator.id,
        is_deleted=False
    )
    for _ in range(0, 3):
        post = await PostsFactory(creator_id=creator.id, id=randint(0, 10000))
        posts_redis_factory(creator.id, "subscriber", PostsModel(**{k: v for k, v in post.__dict__.items()}))
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get(
            "/feed/subscriber/", headers=AUTH_HEADERS, params={"subscriber_id": subscriber.id}
        )
    assert response.status_code == 200
    response_data = response.json()
    assert type(response_data) == dict
    assert "feed_type" in response_data
    assert response_data["feed_type"] == "subscriber"
    assert "posts" in response_data
    assert type(response_data["posts"]) == list
    assert len(response_data["posts"]) == 3
    assert response_data["posts"][0]["creator_id"] == str(creator.id)


@pytest.mark.asyncio
async def test_get_creator_feed():
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    await UserSubscriptionsFactory(
        creator_id=creator.id,
        subscriber_id=subscriber.id
    )
    for _ in range(0, 3):
        post = await PostsFactory(creator_id=creator.id, id=randint(0, 10000))
        post_model = PostsModel(**{k: v for k, v in post.__dict__.items()})
        posts_redis_factory(creator.id, "creator", post_model)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/feed/creator/", headers=AUTH_HEADERS, params={"creator_id": creator.id})
    assert response.status_code == 200
    response_data = response.json()
    assert type(response_data) == dict
    assert "feed_type" in response_data
    assert response_data["feed_type"] == "creator"
    assert "posts" in response_data
    assert type(response_data["posts"]) == list
    assert len(response_data["posts"]) == 3
    assert response_data["posts"][0]["creator_id"] == str(creator.id)


@pytest.mark.asyncio
async def test_get_discovery_feed():
    creator = await UsersFactory()
    subscriber = await UsersFactory()
    await UserSubscriptionsFactory(
        creator_id=creator.id,
        subscriber_id=subscriber.id
    )
    for _ in range(0, 3):
        post = await PostsFactory(creator_id=creator.id, id=randint(0, 10000))
        post_model = PostsModel(**{k: v for k, v in post.__dict__.items()})
        posts_redis_factory(creator.id, "discovery", post_model)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/feed/discovery/", headers=AUTH_HEADERS, params={"user_id": subscriber.id})
    assert response.status_code == 200
    response_data = response.json()
    assert type(response_data) == dict
    assert "feed_type" in response_data
    assert response_data["feed_type"] == "discovery"
    assert "posts" in response_data
    assert type(response_data["posts"]) == list
    assert len(response_data["posts"]) == 3
    assert response_data["posts"][0]["creator_id"] == str(creator.id)
