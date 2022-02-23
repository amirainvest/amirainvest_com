import typing as t
from typing import List

from fastapi import APIRouter, Depends, File, status, UploadFile

from backend_amirainvest_com.api.backend.post_route.controller import (
    create_controller,
    get_controller,
    list_controller,
    update_controller,
    upload_post_photo_controller,
)
from backend_amirainvest_com.api.backend.post_route.model import (
    CreateModel,
    GetInputModel,
    GetResponseModel,
    ListInputModel,
    ListReturnModel,
    UpdateModel,
    UploadPhotosModel,
)
from backend_amirainvest_com.controllers.auth import auth_depends_user_id
from common_amirainvest_com.schemas.schema import PostsModel


router = APIRouter(prefix="/post", tags=["Post"])


# ALL PLATFORM POSTS GENERATED VIA DATA IMPORTS


@router.post(
    "/get", status_code=status.HTTP_200_OK, response_model=t.List[GetResponseModel], response_model_exclude_none=True
)
async def get_route(
    get_input: GetInputModel,
    token=Depends(auth_depends_user_id),
):
    post_id_list = get_input.ids
    data = await get_controller(subscriber_id=token["https://amirainvest.com/user_id"], post_id_list=post_id_list)
    return data


@router.post("/list", status_code=status.HTTP_200_OK, response_model=ListReturnModel, response_model_exclude_none=True)
async def list_route(list_request: ListInputModel, token=Depends(auth_depends_user_id)):
    data: t.List[GetResponseModel] = await list_controller(
        subscriber_id=token["https://amirainvest.com/user_id"],
        list_request=list_request,
    )
    results = ListReturnModel(results=data, result_count=len(data))
    return results


@router.post("/create", status_code=status.HTTP_200_OK, response_model=PostsModel)
async def create_route(
    post_data: CreateModel,
    token=Depends(auth_depends_user_id),
):
    return (
        await create_controller(
            user_id=token["https://amirainvest.com/user_id"],
            create_data=post_data,
        )
    )._asdict()


@router.post("/update", status_code=status.HTTP_200_OK, response_model=PostsModel)
async def update_route(
    post_data: UpdateModel,
    token=Depends(auth_depends_user_id),
):
    return (
        await update_controller(
            user_id=token["https://amirainvest.com/user_id"],
            update_data=post_data,
        )
    )._asdict()


@router.post("/upload/post_photos", status_code=status.HTTP_200_OK, response_model=UploadPhotosModel)
async def upload_post_photos_route(
    images: List[UploadFile] = File(...),
    token=Depends(auth_depends_user_id),
):
    photo_urls = [
        upload_post_photo_controller(
            image.file.read(), image.filename, user_id=token["https://amirainvest.com/user_id"]
        )
        for image in images
    ]

    return UploadPhotosModel(photos=photo_urls)
