pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]
import pytest

from .config import client


@pytest.mark.asyncio
async def test_non_authenticated_user_get_code_challenge():
    response = client.get("/code_challenge/")
    assert response.status_code == 200
