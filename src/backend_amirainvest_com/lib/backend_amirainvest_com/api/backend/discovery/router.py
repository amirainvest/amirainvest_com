from typing import List

from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.discovery.controller import get_controller
from backend_amirainvest_com.api.backend.discovery.model import GetModel
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/discovery", tags=["Discovery"])


@router.post("/get", status_code=status.HTTP_200_OK, response_model=List[GetModel])
async def get_route(token=Depends(auth_depends_user_id)):
    data = await get_controller()
    return data
