import typing as t
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as

from backend_amirainvest_com.api.backend.platform.controller import (
    check_platforms,
    claim_platforms,
    create_platforms,
    error_if_collision,
    get_controller,
    update_platform_usernames,
    delete_platforms
)
from backend_amirainvest_com.api.backend.platform.model import (
    CreatePlatformModel,
    DeletePlatformModel,
    Http409Enum,
    Http409Model,
    PlatformModel
)
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/platforms", tags=["Platform Users/Claims"])


@router.post(
    "/get", status_code=status.HTTP_200_OK, response_model=List[PlatformModel], response_model_exclude_none=True
)
async def get_platforms_route(token=Depends(auth_depends_user_id)):
    return await get_controller(user_id=token["https://amirainvest.com/user_id"])


@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    response_model=List[CreatePlatformModel],
    response_model_exclude_none=True,
    responses={
        status.HTTP_409_CONFLICT: {"model": Http409Model, "description": "Collision with platforms being created"}
    },
)
async def create_platforms_route(platform_data: List[PlatformModel], token=Depends(auth_depends_user_id)):
    claimed_platforms, unclaimed_platforms, not_exist = await check_platforms(platform_data)
    await error_if_collision(claimed_platforms, unclaimed_platforms, platform_data)
    user_id = token["https://amirainvest.com/user_id"]
    return await create_platforms(user_id, platform_data)


@router.post(
    "/claim", 
    status_code=status.HTTP_200_OK, 
    response_model=List[CreatePlatformModel], 
    response_model_exclude_none=True,
    responses={
        status.HTTP_409_CONFLICT: {"model": Http409Model, "description": "Collision with platforms being claimed"}
    }
)
async def claim_platforms_route(platform_data: List[PlatformModel], token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    claimed_platforms, unclaimed_platforms, not_exist = await check_platforms(platform_data)
    if len(claimed_platforms)>0:
        models = parse_obj_as(t.List[CreatePlatformModel], claimed_platforms)
        error = Http409Enum.platforms_match_claimed_user.value.dict()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"platforms": jsonable_encoder([x.dict() for x in models]), **error},
        )
    return await claim_platforms(platform_data, user_id)
    #TODO: make sure that accounts are only being claimed from husks, not a claimed user. 
    # Add where clause User.is_claimed.is_(False) in SQL, don't rely on check_platforms() above


@router.post(
    "/update",
    status_code=status.HTTP_200_OK,
    response_model=List[CreatePlatformModel],
    response_model_exclude_none=True,
    responses={
        status.HTTP_409_CONFLICT: {"model": Http409Model, "description": "Collision with platforms being updated"}
    }
)
async def update_platforms_route(platform_data: List[PlatformModel], token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    claimed_platforms, unclaimed_platforms, not_exist = await check_platforms(platform_data)
    await error_if_collision(claimed_platforms, unclaimed_platforms, platform_data)    
    return await update_platform_usernames(user_id, platform_data)


@router.post(
    "/delete",
    status_code=status.HTTP_200_OK,
)
async def delete_platforms_route(platform_data: List[DeletePlatformModel], token=Depends(auth_depends_user_id)):
    # will need to check for collisions here too. FE will need to re-verify
    user_id = token["https://amirainvest.com/user_id"]
    claimed_platforms, unclaimed_platforms, not_exist = await check_platforms(platform_data)
    return delete_platforms(platform_data, user_id)
