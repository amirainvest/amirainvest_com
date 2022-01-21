from uuid import UUID

from fastapi import APIRouter, status

from backend_amirainvest_com.api.backend.user_feedback.controller import create_controller
from backend_amirainvest_com.api.backend.user_feedback.model import CreateModel, GetModel
from backend_amirainvest_com.controllers.auth import auth_depends, Depends


router = APIRouter(prefix="/user_feedback", tags=["User Feedback"])


@router.post("/create", status_code=status.HTTP_200_OK, response_model=GetModel)
async def create_route(feedback_data: CreateModel, token=Depends(auth_depends)):
    user_id: UUID = token["https://amirainvest.com/user_id"]
    user_feedback = await create_controller(user_id, feedback_data)
    user_feedback = user_feedback.dict()
    return user_feedback
