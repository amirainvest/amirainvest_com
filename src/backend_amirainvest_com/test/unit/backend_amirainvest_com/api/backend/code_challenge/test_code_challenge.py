

from httpx import AsyncClient

from backend_amirainvest_com.api.app import app


async def test_non_authenticated_user_get_code_challenge():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/code_challenge")
    assert response.status_code == 200
    response_data = response.json()
    assert type(response_data) == dict
    assert "verify" in response_data
    assert "challenge" in response_data
