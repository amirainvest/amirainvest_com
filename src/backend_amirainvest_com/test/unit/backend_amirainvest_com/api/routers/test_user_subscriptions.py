from httpx import AsyncClient

from backend_amirainvest_com.api.app import app

from ..config import AUTH_HEADERS


async def test_not_authenticated_get_user_subscriptions():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/user_subscriptions/subscriber")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


async def test_get_subscriptions_for_subscriber(factory):
    subscriber = await factory.gen("users")
    creator = await factory.gen("users")
    await factory.gen(
        "user_subscriptions",
        {"user_subscriptions": {"creator_id": creator["users"].id, "subscriber_id": subscriber["users"].id}},
    )
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get(
            "/user_subscriptions/subscriber", params={"subscriber_id": subscriber["users"].id}, headers=AUTH_HEADERS
        )
    assert response.status_code == 200
    assert str(creator["users"].id) in [x["creator_id"] for x in response.json()]


async def test_get_subscriptions_for_creator(factory):
    subscriber = await factory.gen("users")
    creator = await factory.gen("users")
    await factory.gen(
        "user_subscriptions",
        {"user_subscriptions": {"creator_id": creator["users"].id, "subscriber_id": subscriber["users"].id}},
    )
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get(
            "/user_subscriptions/creator", params={"creator_id": creator["users"].id}, headers=AUTH_HEADERS
        )
    assert response.status_code == 200
    assert str(subscriber["users"].id) in [x["subscriber_id"] for x in response.json()]


async def test_create_subscription(factory):
    subscriber = await factory.gen("users")
    creator = await factory.gen("users")
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/user_subscriptions/subscribe",
            headers=AUTH_HEADERS,
            params={
                "subscriber_id": str(subscriber["users"].id),
                "creator_id": str(creator["users"].id),
            },
        )
    assert response.status_code == 200
