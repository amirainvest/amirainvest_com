import pytest


pytestmark = [pytest.mark.unit_test]

@pytest.fixture(scope="function", autouse=True)
async def autouse_mock_auth(mock_auth):
    pass
