import json

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


# TODO add tests:
#   Check pageing
#   Check getting the correct posts if more posts than max
#   Check getting the correct posts when last_loaded_post_id passed
#   Check getting the correct data when multiple subscribers and creators (creator, sub, and discovery feed)
#   Check discovery feed filtering out user posts (last_load_post_id passed). All posts read
#   Check more posts than max_feed_size
#   Check more posts than max_feed_size and last_load_post_id


async def test_create(async_session_maker_test, factory):
    session_test: AsyncSession = async_session_maker_test()
    user = await factory.gen("users")
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/post/create",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "platform": "twitter",
                    "platform_user_id": "test",
                    "platform_post_id": "test",
                    "profile_img_url": "test",
                    "text": "test",
                    "html": "test",
                    "title": "test",
                    "profile_url": "test",
                }
            ),
            params={"user_id": user["users"].id},
        )

    assert response.status_code == 200
    result = response.json()

    assert result["text"] == "test"

    db_result = (await session_test.execute(select(Posts))).scalars().one()

    assert db_result.platform_user_id == "test"


async def test_update(async_session_maker_test, factory):
    session_test: AsyncSession = async_session_maker_test()

    post = await factory.gen("posts")

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/post/update",
            headers=AUTH_HEADERS,
            data=json.dumps(
                {
                    "id": post["posts"].id,
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
            params={"user_id": post["users"].id},
        )
    assert response.status_code == 200
    result = response.json()

    assert result["platform_user_id"] == "updated"

    db_result = (await session_test.execute(select(Posts))).scalars().one()

    assert db_result.platform_user_id == "updated"


async def test_list_subscriber_feed(mock_auth, factory):
    creator = await factory.gen("users")
    subscriber = await factory.gen("users")
    await factory.gen(
        "user_subscriptions", {
            "user_subscriptions": {
                "creator_id": creator["users"].id,
                "subscriber_id": subscriber["users"].id
            },
        }
    )
    await mock_auth(subscriber["users"].id)
    for _ in range(0, PAGE_SIZE):
        post = await factory.gen("posts", {"posts": {"creator_id": creator["users"].id}})
        posts_redis_factory(subscriber["users"].id, FeedType.subscriber.value, PostsModel(**post["posts"].__dict__))

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
    assert all([response["creator_id"] == str(creator["users"].id) for response in response_data["posts"]])


async def test_list_subscriber_feed_no_cache(mock_auth, factory):
    creator = await factory.gen("users")
    subscriber = await factory.gen("users")
    await factory.gen(
        "user_subscriptions", {
            "user_subscriptions": {
                "creator_id": creator["users"].id,
                "subscriber_id": subscriber["users"].id
            },
        }
    )
    await mock_auth(subscriber["users"].id)

    for _ in range(0, PAGE_SIZE):
        await factory.gen("posts", {"posts": {"creator_id": creator["users"].id}})

    redis_feed = get_redis_feed(str(subscriber["users"].id), FeedType.subscriber)
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
    assert all([response["creator_id"] == str(creator["users"].id) for response in response_data["posts"]])

    redis_feed = get_redis_feed(str(subscriber["users"].id), FeedType.subscriber)
    assert len(redis_feed) == PAGE_SIZE


async def test_list_empty_subscriber_feed(mock_auth, factory):
    creator = await factory.gen("users")
    subscriber = await factory.gen("users")
    await factory.gen(
        "user_subscriptions", {
            "user_subscriptions": {
                "creator_id": creator["users"].id,
                "subscriber_id": subscriber["users"].id
            },
        }
    )
    await mock_auth(subscriber["users"].id)

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


async def test_get_creator_feed(factory):
    creator = await factory.gen("users")

    for _ in range(0, PAGE_SIZE):
        post = await factory.gen("posts", {"posts": {"creator_id": creator["users"].id}})
        posts_redis_factory(
            str(creator["users"].id), FeedType.creator.value, PostsModel.parse_obj(post["posts"].dict())
        )

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/post/list",
            headers=AUTH_HEADERS,
            data=json.dumps({"feed_type": FeedType.creator.value, "creator_id": str(creator["users"].id)}),
        )

    response_data = response.json()
    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list
    assert response_data["feed_type"] == FeedType.creator.value

    assert len(response_data["posts"]) == PAGE_SIZE
    assert all([response["creator_id"] == str(creator["users"].id) for response in response_data["posts"]])


async def test_get_creator_feed_no_cache(factory):
    creator = await factory.gen("users")

    for _ in range(0, PAGE_SIZE):
        post = await factory.gen("posts", {"posts": {"creator_id": creator["users"].id}})

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/post/list",
            headers=AUTH_HEADERS,
            data=json.dumps({"feed_type": FeedType.creator.value, "creator_id": str(creator["users"].id)}),
        )

    response_data = response.json()
    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list
    assert response_data["feed_type"] == FeedType.creator.value

    assert len(response_data["posts"]) == PAGE_SIZE
    assert all([response["creator_id"] == str(creator["users"].id) for response in response_data["posts"]])


async def test_get_empty_creator_feed(factory):
    creator = await factory.gen("users")

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/post/list",
            headers=AUTH_HEADERS,
            data=json.dumps({"feed_type": FeedType.creator.value, "creator_id": str(creator["users"].id)}),
        )

    response_data = response.json()
    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list

    assert response_data["feed_type"] == FeedType.creator.value

    assert len(response_data["posts"]) == 0


async def test_get_discovery_feed(factory):
    creator = await factory.gen("users")

    for _ in range(0, PAGE_SIZE):
        post = await factory.gen("posts", {"posts": {"creator_id": creator["users"].id}})
        posts_redis_factory(
            FeedType.discovery.value, FeedType.discovery.value, PostsModel.parse_obj(post["posts"].dict())
        )

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/post/list",
            headers=AUTH_HEADERS,
            data=json.dumps({"feed_type": FeedType.discovery.value}),
        )

    response_data = response.json()
    assert response.status_code == 200

    assert type(response_data) == dict
    assert type(response_data["posts"]) == list

    assert response_data["feed_type"] == FeedType.discovery.value
    assert len(response_data["posts"]) == PAGE_SIZE

    assert all([response["creator_id"] == str(creator["users"].id) for response in response_data["posts"]])
