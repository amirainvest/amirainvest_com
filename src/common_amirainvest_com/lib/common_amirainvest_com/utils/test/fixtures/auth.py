import pytest

from common_amirainvest_com.utils.test.fixtures.consts import FAKE_USER_UUID


@pytest.fixture(scope="function", autouse=False)
async def mock_auth(monkeypatch):
    async def _mock_auth(user_id: str):
        async def auth_dep_mock(*args, **kwargs):
            return {
                "https://amirainvest.com/user_id": user_id,
                "sub": "fake_sub",
            }

        from backend_amirainvest_com.controllers import auth

        monkeypatch.setattr(auth, "_auth_dep", auth_dep_mock)

    await _mock_auth(FAKE_USER_UUID)

    yield _mock_auth


@pytest.fixture(scope="function", autouse=False)
async def mock_auth_no_user_id(monkeypatch):
    async def _mock_auth():
        async def auth_dep_mock(*args, **kwargs):
            return {
                "sub": "fake_sub",
            }

        from backend_amirainvest_com.controllers import auth

        monkeypatch.setattr(auth, "_auth_dep", auth_dep_mock)

    await _mock_auth()

    yield _mock_auth
