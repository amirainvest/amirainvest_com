pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]

import pytest
from httpx import AsyncClient

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.utils.test.factories.schema import UsersFactory, UserSubscriptionsFactory

from .config import AUTH_HEADERS


@pytest.mark.asyncio
async def test_not_authenticated_get_user_subscriptions():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/user_subscriptions/subscriber/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_subscriptions_for_subscriber():
    subscriber = await UsersFactory()
    creator = await UsersFactory()
    await UserSubscriptionsFactory(creator_id=creator.id, subscriber_id=subscriber.id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get(
            "/user_subscriptions/subscriber/", params={"subscriber_id": subscriber.id}, headers=AUTH_HEADERS
        )
    assert response.status_code == 200
    assert str(creator.id) in [x["creator_id"] for x in response.json()]


@pytest.mark.asyncio
async def test_get_subscriptions_for_creator():
    subscriber = await UsersFactory()
    creator = await UsersFactory()
    await UserSubscriptionsFactory(creator_id=creator.id, subscriber_id=subscriber.id)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get(
            "/user_subscriptions/creator/", params={"creator_id": creator.id}, headers=AUTH_HEADERS
        )
    assert response.status_code == 200
    assert str(subscriber.id) in [x["subscriber_id"] for x in response.json()]


@pytest.mark.asyncio
async def test_create_subscription():
    subscriber = await UsersFactory()
    creator = await UsersFactory()
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/user_subscriptions/subscribe/",
            headers=AUTH_HEADERS,
            params={
                "subscriber_id": str(subscriber.id),
                "creator_id": str(creator.id),
            },
        )
    assert response.status_code == 200
