import typing as t
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as

from backend_amirainvest_com.api.backend.platform.controller import (
    check_platforms,
    claim_platforms,
    create_platforms,
    get_controller,
)
from backend_amirainvest_com.api.backend.platform.model import (
    CreatePlatformModel,
    Http409Enum,
    Http409Model,
    PlatformModel,
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
        status.HTTP_409_CONFLICT: {"model": Http409Model, "description": "Collision with platforms being claimed"}
    },
)
async def create_platforms_route(platform_data: List[PlatformModel], token=Depends(auth_depends_user_id)):
    claimed_platforms, unclaimed_platforms = await check_platforms(platform_data)
    if len(claimed_platforms) > 0:
        models = parse_obj_as(t.List[CreatePlatformModel], claimed_platforms)
        error = Http409Enum.platforms_match_claimed_user.value.dict()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"platforms": jsonable_encoder([x.dict() for x in models]), **error},
        )

    elif len(unclaimed_platforms) > 0:
        error = Http409Enum.platforms_match_unclaimed_husk.value.dict()
        models = parse_obj_as(t.List[CreatePlatformModel], unclaimed_platforms)
        for model in models:
            model.is_claimed = False
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"platforms": jsonable_encoder([x.dict() for x in models]), **error},
        )

    user_id = token["https://amirainvest.com/user_id"]
    return await create_platforms(user_id, platform_data)


@router.post(
    "/claim", status_code=status.HTTP_200_OK, response_model=List[CreatePlatformModel], response_model_exclude_none=True
)
async def claim_platforms_route(platform_data: List[PlatformModel], token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    return await claim_platforms(platform_data, user_id)


@router.post(
    "/update",
    status_code=status.HTTP_200_OK,
    response_model=List[CreatePlatformModel],
    response_model_exclude_none=True,
)
async def update_platforms_route():
    # have an is_deleted field here
    # will need to check for collisions here too. FE will need to re-verify
    pass
