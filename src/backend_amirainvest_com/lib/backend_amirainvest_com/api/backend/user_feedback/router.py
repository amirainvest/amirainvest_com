from fastapi import APIRouter, status

from backend_amirainvest_com.api.backend.user_feedback.controller import create_controller
from backend_amirainvest_com.api.backend.user_feedback.model import CreateModel
from backend_amirainvest_com.controllers.auth import auth_depends, Depends


router = APIRouter(prefix="/user_feedback", tags=["User Feedback"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_route(feedback_data: CreateModel, token=Depends(auth_depends)):
    user_id: str = token["https://amirainvest.com/user_id"]
    await create_controller(user_id, feedback_data)
