from httpx import AsyncClient

from backend_amirainvest_com.api.app import app

from ..config import AUTH_HEADERS


async def test_not_authenticated_get_search_results():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/search/recent_content")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


async def test_search_recent_content():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/search/recent_content", headers=AUTH_HEADERS)
    assert response.status_code == 200


async def test_search_users():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/search/users", headers=AUTH_HEADERS)
    assert response.status_code == 200


async def test_search_like_content():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/search/content", headers=AUTH_HEADERS, params={"search_term": "TEST"})
    assert response.status_code == 200


async def test_get_like_creators():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/search/creators", headers=AUTH_HEADERS, params={"search_term": "TEST"})
    assert response.status_code == 200
