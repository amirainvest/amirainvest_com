import json

from fastapi import status
from httpx import AsyncClient

from backend_amirainvest_com.api.app import app
from backend_amirainvest_com.api.backend.feed_route.model import FeedType
from common_amirainvest_com.utils.query_fragments.feed import PAGE_SIZE

from ...config import AUTH_HEADERS


# TODO add tests:
#   Check pageing
#   Check getting the correct posts if more posts than max
#   Check getting the correct posts when last_loaded_post_id passed
#   Check getting the correct data when multiple subscribers and creators (creator, sub, and discovery feed)
#   Check discovery feed filtering out user posts (last_load_post_id passed). All posts read
#   Check more posts than max_feed_size
#   Check more posts than max_feed_size and last_load_post_id


async def test_list_subscriber_feed(mock_auth, factory):
    creator = await factory.gen("users")
    subscriber = await factory.gen("users")
    await factory.gen(
        "user_subscriptions",
        {
            "user_subscriptions": {"creator_id": creator["users"].id, "subscriber_id": subscriber["users"].id},
        },
    )
    await mock_auth(subscriber["users"].id)

    for _ in range(0, PAGE_SIZE):
        await factory.gen("posts", {"posts": {"creator_id": creator["users"].id}})

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/feed/get",
            headers=AUTH_HEADERS,
            data=json.dumps({"feed_type": FeedType.subscriber.value}),
        )

    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert type(response_data) == dict
    assert type(response_data["posts"]) == list

    assert response_data["feed_type"] == FeedType.subscriber.value
    assert len(response_data["posts"]) == PAGE_SIZE
    assert all([response["creator"]["id_creator"] == str(creator["users"].id) for response in response_data["posts"]])


async def test_list_empty_subscriber_feed(mock_auth, factory):
    creator = await factory.gen("users")
    subscriber = await factory.gen("users")
    await factory.gen(
        "user_subscriptions",
        {
            "user_subscriptions": {"creator_id": creator["users"].id, "subscriber_id": subscriber["users"].id},
        },
    )
    await mock_auth(subscriber["users"].id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/feed/get",
            headers=AUTH_HEADERS,
            data=json.dumps({"feed_type": FeedType.subscriber.value}),
        )

    response_data = response.json()
    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list
    assert len(response_data["posts"]) == 0
    assert response_data["feed_type"] == FeedType.discovery.value


async def test_get_creator_feed(factory):
    creator = await factory.gen("users")

    for _ in range(0, PAGE_SIZE):
        await factory.gen("posts", {"posts": {"creator_id": creator["users"].id}})

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/feed/get",
            headers=AUTH_HEADERS,
            data=json.dumps({"feed_type": FeedType.creator.value, "creator_id": str(creator["users"].id)}),
        )

    response_data = response.json()
    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list
    assert response_data["feed_type"] == FeedType.creator.value

    assert len(response_data["posts"]) == PAGE_SIZE
    assert all([response["creator"]["id_creator"] == str(creator["users"].id) for response in response_data["posts"]])


async def test_get_empty_creator_feed(factory):
    creator = await factory.gen("users")

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/feed/get",
            headers=AUTH_HEADERS,
            data=json.dumps({"feed_type": FeedType.creator.value, "creator_id": str(creator["users"].id)}),
        )

    response_data = response.json()
    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list

    assert response_data["feed_type"] == FeedType.discovery.value

    assert len(response_data["posts"]) == 0


async def test_get_discovery_feed(factory):
    creator = await factory.gen("users")
    for _ in range(0, PAGE_SIZE + 10):
        await factory.gen("posts", {"posts": {"creator_id": creator["users"].id}})

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/feed/get",
            headers=AUTH_HEADERS,
            data=json.dumps({"feed_type": FeedType.discovery.value}),
        )

    response_data = response.json()
    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list

    assert response_data["feed_type"] == FeedType.discovery.value
    assert len(response_data["posts"]) == PAGE_SIZE

    assert all([response["creator"]["id_creator"] == str(creator["users"].id) for response in response_data["posts"]])


async def test_get_discovery_feed_filter_out_subscribed_posts(factory, mock_auth):
    page_size = 20
    creator = await factory.gen("users")
    for _ in range(0, page_size - 5):
        await factory.gen("posts", {"posts": {"creator_id": creator["users"].id}})

    subscriber = await factory.gen("users")
    creator_sub_to = await factory.gen("users")
    await factory.gen(
        "user_subscriptions",
        {
            "user_subscriptions": {
                "creator_id": creator_sub_to["users"].id,
                "subscriber_id": subscriber["users"].id,
            },
        },
    )
    await factory.gen("posts", {"posts": {"creator_id": creator_sub_to["users"].id}})
    await factory.gen("posts", {"posts": {"creator_id": creator_sub_to["users"].id}})
    await mock_auth(subscriber["users"].id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/feed/get",
            headers=AUTH_HEADERS,
            data=json.dumps({"feed_type": FeedType.discovery.value, "page_size": page_size}),
        )

    response_data = response.json()
    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list

    assert response_data["feed_type"] == FeedType.discovery.value
    assert len(response_data["posts"]) == page_size - 5

    assert all([response["creator"]["id_creator"] == str(creator["users"].id) for response in response_data["posts"]])
