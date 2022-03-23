from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile

from backend_amirainvest_com.api.backend.user_route.controller import (
    create_controller,
    deactivate_controller,
    delete_controller,
    get_controller,
    list_controller,
    reactivate_controller,
    update_controller,
    update_controller_profile_pic,
)
from backend_amirainvest_com.api.backend.user_route.model import (
    DeleteUserModel,
    GetReturnModel,
    Http400Model,
    Http409Enum,
    Http409Model,
    InitPostModel,
    InitReturnModel,
    ListInputModel,
    ListReturnModel,
    UserUpdate,
)
from backend_amirainvest_com.controllers import uploads
from backend_amirainvest_com.controllers.auth import auth_depends, auth_depends_user_id


router = APIRouter(prefix="/user", tags=["User"])


@router.post("/get", status_code=status.HTTP_200_OK, response_model=GetReturnModel)
async def get_route(user_id: str, token=Depends(auth_depends_user_id)):
    return (
        await get_controller(
            user_id,
        )
    ).__dict__


@router.post("/list", status_code=200, response_model=ListReturnModel, response_model_exclude_none=True)
async def list_route(list_request: ListInputModel, token=Depends(auth_depends_user_id)):
    all_users = await list_controller(list_request)
    results = ListReturnModel(
        results=all_users,
        result_count=len(all_users),
    )
    return results


@router.post("/update", status_code=status.HTTP_200_OK, response_model=GetReturnModel)
async def update_route(user_data: UserUpdate, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    response = await update_controller(user_id=user_id, user_data=user_data)
    return response._asdict()


@router.post("/upload/profile_picture", status_code=status.HTTP_200_OK, response_model=GetReturnModel)
async def upload_profile_picture_route(image: UploadFile = File(...), token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    s3_file_url = uploads.upload_profile_photo(image.file.read(), image.filename, user_id)
    return (await update_controller_profile_pic(user_id=user_id, s3_url=s3_file_url))._asdict()


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
    user_id = token.get("https://amirainvest.com/user_id")
    if user_id is not None:
        await reactivate_controller(user_id=user_id, sub=sub)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=Http409Enum.app_metadata_includes_user_id.value.dict(),
        )

    user_id = await create_controller(
        user_data,
        sub,
    )
    return InitReturnModel(id=user_id)


@router.post("/delete", status_code=status.HTTP_200_OK, response_model=GetReturnModel)
async def delete_route(action: DeleteUserModel, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    sub = token["sub"]
    if action.delete_action.value == "deactivate":
        response = await deactivate_controller(user_id, sub)
    elif action.delete_action.value == "delete":
        response = await delete_controller(user_id, sub)
    return response
