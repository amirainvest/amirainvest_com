from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.user_feedback.model import CreateModel
from common_amirainvest_com.schemas.schema import UserFeedback
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_controller(session: AsyncSession, user_feedback_data: CreateModel):
    user_feedback = UserFeedback(**user_feedback_data.dict(exclude_none=True))
    session.add(user_feedback)
    return user_feedback
