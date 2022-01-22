from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.user_feedback.model import CreateModel
from common_amirainvest_com.schemas.schema import UserFeedback
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_controller(session: AsyncSession, user_id: UUID, user_feedback_data: CreateModel) -> UserFeedback:
    feedback_data = user_feedback_data.dict(exclude_none=True)
    feedback_data["user_id"] = user_id
    user_feedback = UserFeedback(**feedback_data)
    session.add(user_feedback)
    return user_feedback
