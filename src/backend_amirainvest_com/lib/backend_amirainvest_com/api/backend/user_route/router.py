import uuid

from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile

from backend_amirainvest_com.api.backend.user_route.controller import (
    create_controller,
    delete_controller,
    get_controller,
    update_controller,
)
from backend_amirainvest_com.api.backend.user_route.model import (
    Http400Model,
    Http409Enum,
    Http409Model,
    InitPostModel,
    InitReturnModel,
    UserUpdate,
)
from backend_amirainvest_com.controllers import uploads
from backend_amirainvest_com.controllers.auth import auth_depends
from common_amirainvest_com.schemas.schema import UsersModel


router = APIRouter(prefix="/user", tags=["User"])


@router.post("/get", status_code=status.HTTP_200_OK, response_model=UsersModel)
async def get_route(user_id: uuid.UUID, token=Depends(auth_depends)):
    return (
        await get_controller(
            user_id,
        )
    ).__dict__


@router.post("/update", status_code=status.HTTP_200_OK, response_model=UsersModel)
async def update_route(user_id: uuid.UUID, user_data: UserUpdate, token=Depends(auth_depends)):
    return (await update_controller(user_id=user_id, user_data=user_data))._asdict()


@router.post("/upload/profile_picture", status_code=status.HTTP_200_OK, response_model=UsersModel)
async def upload_profile_picture_route(user_id: uuid.UUID, image: UploadFile = File(...), token=Depends(auth_depends)):
    s3_file_url = uploads.upload_profile_photo(image.file.read(), image.filename, user_id)
    user = await get_controller(
        user_id,
    )
    user.picture_url = s3_file_url
    return (await update_controller(user.__dict__))._asdict()


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=InitReturnModel,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Http400Model, "description": "Request failed"},
        status.HTTP_409_CONFLICT: {"model": Http409Model, "description": "Data conflict"},
    },
)
async def create_route(user_data: InitPostModel, token=Depends(auth_depends)):
    sub = token["sub"]
    app_metadata = token.get("app_metadata", {})
    if app_metadata.get("user_id") is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=Http409Enum.app_metadata_includes_user_id.value.dict(),
        )

    user_id = await create_controller(
        user_data,
        sub,
    )
    return InitReturnModel(id=user_id)


@router.post("/delete", status_code=status.HTTP_200_OK)
async def delete_route(user_id: uuid.UUID, token=Depends(auth_depends)):
    sub = token["sub"]
    await delete_controller(user_id, sub)
