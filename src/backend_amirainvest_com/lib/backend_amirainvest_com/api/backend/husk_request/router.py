from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.husk_request.controller import create_controller, delete_controller
from backend_amirainvest_com.api.backend.husk_request.model import CreateModel, GetModel
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/husk_request", tags=["Husk Request"])


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=GetModel)
async def create_route(
    husk_request_data: CreateModel,
    token=Depends(auth_depends_user_id)
):
    husk_request = await create_controller(husk_request_data)
    husk_request = husk_request.dict()
    return husk_request


@router.post("/delete", status_code=status.HTTP_200_OK)
async def delete_route(
    husk_request_id: int,
    token=Depends(auth_depends_user_id)):
    await delete_controller(husk_request_id)
