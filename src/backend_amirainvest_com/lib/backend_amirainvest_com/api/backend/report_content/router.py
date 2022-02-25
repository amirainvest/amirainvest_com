from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.report_content.controller import create_controller

from backend_amirainvest_com.api.backend.report_content.model import ReportPostModel
from backend_amirainvest_com.controllers.auth import auth_depends_user_id

router = APIRouter(prefix="/report-content", tags=["Report Inappropriate Content"])


@router.post(
    "/create",
    summary="Create Content Report Record for a Post",
    status_code=status.HTTP_200_OK,
    response_model=ReportPostModel
    )
async def create_route(post_id: int, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    return create_controller(user_id, post_id)


