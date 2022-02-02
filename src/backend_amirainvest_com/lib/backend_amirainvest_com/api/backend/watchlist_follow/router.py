import uuid
from typing import List

from fastapi import APIRouter, Security, status

from backend_amirainvest_com.api.backend.watchlist_follow.controller import (
    create_controller,
    delete_controller,
    get_controller,
    list_controller,
)
from backend_amirainvest_com.api.backend.watchlist_follow.model import CreateModel, FollowedWatchlistModel, GetModel
from backend_amirainvest_com.controllers.auth import auth_dep


router = APIRouter(prefix="/watchlist_follow", tags=["Watchlist Follow"], dependencies=[Security(auth_dep, scopes=[])])


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=GetModel)
async def create_route(watchlist_follow_data: CreateModel):
    return await create_controller(watchlist_follow_data)


@router.post("/get", status_code=status.HTTP_200_OK, response_model=GetModel)
async def get_route(watchlist_follow_id: int):
    return await get_controller(watchlist_follow_id)


@router.post("/list", status_code=status.HTTP_200_OK, response_model=List[FollowedWatchlistModel])
async def list_route(follower_id: uuid.UUID):
    # , response_model = List[FollowedWatchlistModel]
    data = await list_controller(follower_id)
    from pprint import pprint

    print("????????????")
    pprint(data)
    print("????????????")
    return data


@router.post("/delete", status_code=status.HTTP_200_OK)
async def delete_route(watchlist_follow_id: int):
    return await delete_controller(watchlist_follow_id)
