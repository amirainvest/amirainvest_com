pytest_plugins = ["common_amirainvest_com.utils.test.fixtures.database"]

import json

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas.schema import UserFeedback
from common_amirainvest_com.utils.test.factories.schema import UsersFactory

from ...config import AUTH_HEADERS


async def test_create_user_feedback(async_session_maker_test, monkeypatch):
    session_test: AsyncSession = async_session_maker_test()
    from backend_amirainvest_com.controllers import auth

    user = await UsersFactory()

    async def auth_dep_mock(*args, **kwargs):
        return {"https://amirainvest.com/user_id": user.id}

    monkeypatch.setattr(auth, "_auth_dep", auth_dep_mock)
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/user_feedback/create",
            headers=AUTH_HEADERS,
            data=json.dumps({"text": "I love your app."}),
        )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["text"] == "I love your app."
    assert response_data["user_id"] == str(user.id)
    user_feedback_data = await session_test.execute(
        select(UserFeedback).where(UserFeedback.user_id == response_data["user_id"])
    )
    user_feedback_data = user_feedback_data.scalars().one()
    assert str(user_feedback_data.user_id) == str(user.id)
