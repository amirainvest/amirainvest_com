from typing import List

from fastapi import APIRouter, Security, status

from backend_amirainvest_com.api.backend.husk_request.controller import (
    create_controller,
    delete_controller,
    list_controller,
)
from backend_amirainvest_com.api.backend.husk_request.model import CreateModel, GetModel
from backend_amirainvest_com.controllers.auth import auth_dep


router = APIRouter(prefix="/husk_request", tags=["Husk Request"], dependencies=[Security(auth_dep, scopes=[])])


@router.post("/list", status_code=status.HTTP_200_OK, response_model=List[GetModel])
async def list_route():
    husk_request = await list_controller()
    husk_request_data = [x.dict() for x in husk_request]
    return husk_request_data


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=GetModel)
async def create_route(
    husk_request_data: CreateModel,
):
    husk_request = await create_controller(husk_request_data)
    husk_request = husk_request.dict()
    return husk_request


@router.post("/delete", status_code=status.HTTP_200_OK)
async def delete_route(husk_request_id: int):
    await delete_controller(husk_request_id)
