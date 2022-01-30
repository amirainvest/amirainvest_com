import uuid
from typing import List

from fastapi import APIRouter, Security, status

from backend_amirainvest_com.api.backend.watchlist_follow.controller import (
    create_controller,
    delete_controller,
    get_controller,
    list_controller,
)
from backend_amirainvest_com.api.backend.watchlist_follow.model import CreateModel, GetModel
from backend_amirainvest_com.controllers.auth import auth_dep


router = APIRouter(prefix="/watchlist_follow", tags=["Watchlist Follow"], dependencies=[Security(auth_dep, scopes=[])])


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=GetModel)
async def create_route(watchlist_follow_data: CreateModel):
    return (await create_controller(watchlist_follow_data)).dict()


@router.post("/get", status_code=status.HTTP_200_OK, response_model=GetModel)
async def get_route(watchlist_follow_id: int):
    return (await get_controller(watchlist_follow_id)).dict()


@router.post("/list", status_code=status.HTTP_200_OK, response_model=List[GetModel])
async def list_route(creator_id: uuid.UUID):
    return (await list_controller(creator_id)).dict()


@router.post("/delete", status_code=status.HTTP_200_OK)
async def delete_route(watchlist_follow_id: int):
    return await delete_controller(watchlist_follow_id)
