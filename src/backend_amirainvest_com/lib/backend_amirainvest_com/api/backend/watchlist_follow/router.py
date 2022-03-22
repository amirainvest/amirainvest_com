from typing import List

from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.watchlist_follow.controller import (
    create_controller,
    delete_controller,
    get_controller,
    list_controller,
)
from backend_amirainvest_com.api.backend.watchlist_follow.model import CreateModel, WatchlistAttributesModel, GetModel
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/watchlist_follow", tags=["Watchlist Follow"])


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=GetModel)
async def create_route(watchlist_follow_data: CreateModel, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    return await create_controller(watchlist_follow_data, user_id)


@router.post("/get", status_code=status.HTTP_200_OK, response_model=GetModel)
async def get_route(watchlist_follow_id: int, token=Depends(auth_depends_user_id)):
    follower_id = token["https://amirainvest.com/user_id"]
    return await get_controller(watchlist_follow_id, follower_id)


@router.post("/list", status_code=status.HTTP_200_OK, response_model=List[WatchlistAttributesModel])
async def list_route(token=Depends(auth_depends_user_id)):
    follower_id = token["https://amirainvest.com/user_id"]
    return await list_controller(follower_id)


@router.post("/delete", status_code=status.HTTP_200_OK)
async def delete_route(watchlist_id: int, token=Depends(auth_depends_user_id)):
    follower_id = token["https://amirainvest.com/user_id"]
    return await delete_controller(watchlist_id, follower_id)
