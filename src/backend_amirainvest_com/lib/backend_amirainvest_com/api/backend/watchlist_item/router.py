from typing import List

from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.watchlist_item.controller import (
    create_controller,
    delete_controller,
    get_controller,
    list_controller,
    update_controller,
)
from backend_amirainvest_com.api.backend.watchlist_item.model import CreateModel, GetModel, UpdateModel
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/watchlist_item", tags=["Watchlist Item"])


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=GetModel)
async def create_route(watchlist_item_data: CreateModel, token=Depends(auth_depends_user_id)):
    creator_id = token["https://amirainvest.com/user_id"]
    return await create_controller(watchlist_item_data, creator_id)


@router.post("/get", status_code=status.HTTP_200_OK, response_model=GetModel)
async def get_route(watchlist_item_id: int, token=Depends(auth_depends_user_id)):
    return await get_controller(watchlist_item_id)


@router.post("/list", status_code=status.HTTP_200_OK, response_model=List[GetModel])
async def list_route(watchlist_id: int, token=Depends(auth_depends_user_id)):
    return await list_controller(watchlist_id)


@router.post("/update", status_code=status.HTTP_200_OK, response_model=GetModel)
async def update_route(watchlist_data: UpdateModel, creator_id: str, token=Depends(auth_depends_user_id)):
    return await update_controller(watchlist_data, creator_id)


@router.post("/delete", status_code=status.HTTP_200_OK)
async def delete_route(watchlist_item_id: int, token=Depends(auth_depends_user_id)):
    creator_id = token["https://amirainvest.com/user_id"]
    return await delete_controller(watchlist_item_id, creator_id)
