from common_amirainvest_com.schemas.schema import UserFeedback
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_controller(session, user_feedback_data):
    user_feedback = UserFeedback(**user_feedback_data.dict(exclude_none=True))
    session.add(user_feedback)
    return user_feedback
