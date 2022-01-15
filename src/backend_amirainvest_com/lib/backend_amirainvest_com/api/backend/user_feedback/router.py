from fastapi import APIRouter, Security, status

from backend_amirainvest_com.api.backend.user_feedback.controller import create_controller
from backend_amirainvest_com.api.backend.user_feedback.model import CreateModel, GetModel
from backend_amirainvest_com.controllers.auth import auth_dep


router = APIRouter(prefix="/user_feedback", tags=["User Feedback"], dependencies=[Security(auth_dep, scopes=[])])


@router.post("", status_code=status.HTTP_200_OK, response_model=GetModel)
async def create_route(feedback_data: CreateModel):
    user_feedback = await create_controller(feedback_data)
    user_feedback = user_feedback.dict()
    return user_feedback
