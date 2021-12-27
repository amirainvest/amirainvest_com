# pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]
#
# from random import randint
#
# import pytest
# from httpx import AsyncClient
#
# from backend_amirainvest_com.api.app import app
# from common_amirainvest_com.utils.test.factories.schema import PostsFactory, UsersFactory, UserSubscriptionsFactory
# from .config import AUTH_HEADERS
#
#
# # TODO: REDIS CONNECTION
# # TODO: TEMP REDIS POSTS
# # TODO: SUBSCRIBER FAN OUT NOT INSTANT...
#
# @pytest.mark.asyncio
# async def test_not_authenticated_get_feed():
#     async with AsyncClient(app=app, base_url="http://test") as async_client:
#         response = await async_client.get("/feed/subscriber/")
#     assert response.status_code == 403
#     assert response.json() == {"detail": "Not authenticated"}
#
#
# @pytest.mark.asyncio
# async def test_get_subscriber_feed():
#     creator = await UsersFactory()
#     subscriber = await UsersFactory()
#     for _ in range(0, 3):
#         await PostsFactory(creator_id=creator.id, id=randint(0, 10000))
#     async with AsyncClient(app=app, base_url="http://test") as async_client:
#         response = await async_client.get(
#             "/feed/subscriber/", headers=AUTH_HEADERS, params={"subscriber_id": subscriber.id}
#         )
#     assert response.status_code == 200
#     response_data = response.json()
#     assert type(response_data) == dict
#     assert "feed_type" in response_data
#     assert "posts" in response_data
#     assert type(response_data["posts"]) == list
#     assert response_data["posts"][0]["creator_id"] == str(creator.id)
#
#
# @pytest.mark.asyncio
# async def test_get_creator_feed():
#     creator = await UsersFactory()
#     subscriber = await UsersFactory()
#     await UserSubscriptionsFactory(
#         creator_id=creator.id,
#         subscriber_id=subscriber.id
#     )
#     await PostsFactory(creator_id=creator.id, id=randint(0, 10000))
#     async with AsyncClient(app=app, base_url="http://test") as async_client:
#         response = await async_client.get("/feed/creator/", headers=AUTH_HEADERS, params={"creator_id": creator.id})
#     assert response.status_code == 200
#     response_data = response.json()
#     assert type(response_data) == dict
#     assert "feed_type" in response_data
#     assert "posts" in response_data
#     assert type(response_data["posts"]) == list
#     assert response_data["posts"][0]["creator_id"] == str(creator.id)
#
#
# @pytest.mark.asyncio
# async def test_get_discovery_feed():
#     creator = await UsersFactory()
#     subscriber = await UsersFactory()
#     await UserSubscriptionsFactory(
#         creator_id=creator.id,
#         subscriber_id=subscriber.id
#     )
#     for _ in range(0, 3):
#         await PostsFactory(creator_id=creator.id, id=randint(0, 10000))
#     async with AsyncClient(app=app, base_url="http://test") as async_client:
#         response = await async_client.get("/feed/discovery/", headers=AUTH_HEADERS, params={"user_id": subscriber.id})
#     assert response.status_code == 200
#     response_data = response.json()
#     assert type(response_data) == dict
#     assert "feed_type" in response_data
#     assert "posts" in response_data
#     assert type(response_data["posts"]) == list
#     assert response_data["posts"][0]["creator_id"] == str(creator.id)
