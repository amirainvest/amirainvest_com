from typing import List
from fastapi import APIRouter, Depends, File, status, UploadFile

from backend_amirainvest_com.platform.model import PlatformModel, CreatePlatformModel
from backend_amirainvest_com.controllers.auth import auth_depends_user_id



router = APIRouter(prefix="/platforms", tags=["Platform Users Claims"])


@router.post(
    "/get", status_code=status.HTTP_200_OK, response_model=List[PlatformModel], response_model_exclude_none=True
)
async def get_platforms_route(token=Depends(auth_depends_user_id)):
    return await get_controller(user_id=token["https://amirainvest.com/user_id"])


@router.post(
    "/create", status_code=status.HTTP_200_OK, response_model=List[CreatePlatformModel], response_model_exclude_none=True
)
async def create_platforms_route(platform_data: t.List[PlatformModel], token=Depends(auth_depends_user_id)):
    unclaimed_user = await check_platforms(platform_data)

    if unclaimed_user: 
        pass