import json

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.app import app
from common_amirainvest_com.schemas.schema import UserFeedback

from ...config import AUTH_HEADERS


async def test_create_user_feedback(async_session_maker_test, mock_auth, factory):
    session_test: AsyncSession = async_session_maker_test()
    user = await factory.gen("users")
    await mock_auth(user["users"].id)

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/user_feedback/create",
            headers=AUTH_HEADERS,
            data=json.dumps({"text": "I love your app."}),
        )

    assert response.status_code == status.HTTP_201_CREATED

    user_feedback_data = await session_test.execute(
        select(UserFeedback).where(UserFeedback.user_id == user["users"].id)
    )
    user_feedback_data = user_feedback_data.scalars().one()
    assert str(user_feedback_data.user_id) == str(user["users"].id)
