from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from backend_amirainvest_com.api.backend.watchlist_item.controller import (
    create_controller,
    delete_controller,
    get_controller,
    list_controller,
    passable_ticker,
    update_controller
)
from backend_amirainvest_com.api.backend.watchlist_item.model import (
    CreateModel,
    GetModel,
    UpdateModel,
    Http409Model,
    Http409Enum,
    Http403Model,
    Http403Enum
)
from backend_amirainvest_com.controllers.auth import auth_depends_user_id
from common_amirainvest_com.controllers.watchlist import get_watchlist_creator


router = APIRouter(prefix="/watchlist_item", tags=["Watchlist Item"])


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=GetModel,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": Http403Model, "description": "Forbidden Request"},
        status.HTTP_409_CONFLICT: {"model": Http409Model, "description": "Conflict with Ticker"}
    }
)
async def create_route(watchlist_item_data: CreateModel, token=Depends(auth_depends_user_id)):
    creator_id = token["https://amirainvest.com/user_id"]
    if (await get_watchlist_creator(watchlist_id=watchlist_item_data.watchlist_id)) != creator_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Http403Enum.not_watchlist_owner.value.dict())
    passable_code = (await passable_ticker(watchlist_item_data.ticker, watchlist_id=watchlist_item_data.watchlist_id))
    if passable_code == 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail = Http409Enum.bad_ticker.value.dict()
        )
    elif passable_code ==1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail = Http409Enum.duplicate_ticker.value.dict()
        )
    return await create_controller(watchlist_item_data)


@router.post("/get", status_code=status.HTTP_200_OK, response_model=GetModel)
async def get_route(watchlist_item_id: int, token=Depends(auth_depends_user_id)):
    return await get_controller(watchlist_item_id)


@router.post("/list", status_code=status.HTTP_200_OK, response_model=List[GetModel])
async def list_route(watchlist_id: int, token=Depends(auth_depends_user_id)):
    return await list_controller(watchlist_id)


@router.post(
    "/update",
    status_code=status.HTTP_200_OK,
    response_model=GetModel,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": Http403Model, "description": "Forbidden Request"}
    }
)
async def update_route(watchlist_item_data: UpdateModel, token=Depends(auth_depends_user_id)):
    creator_id = token["https://amirainvest.com/user_id"]
    if (await get_watchlist_creator(watchlist_item_id=watchlist_item_data.id)) != creator_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Http403Enum.not_watchlist_owner.value.dict())
    return await update_controller(watchlist_item_data)


@router.post(
    "/delete",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": Http403Model, "description": "Forbidden Request"}
    }
)
async def delete_route(watchlist_item_id: int, token=Depends(auth_depends_user_id)):
    creator_id = token["https://amirainvest.com/user_id"]
    if (await get_watchlist_creator(watchlist_item_id=watchlist_item_id)) != creator_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Http403Enum.not_watchlist_owner.value.dict())
    return await delete_controller(watchlist_item_id)
