from typing import List

from fastapi import APIRouter, Depends, File, status, UploadFile

from backend_amirainvest_com.api.backend.post_route.controller import (
    create_controller,
    get_controller,
    update_controller,
    upload_post_photo_controller,
)
from backend_amirainvest_com.api.backend.post_route.model import CreateModel, UpdateModel
from backend_amirainvest_com.controllers.auth import auth_depends_user_id
from common_amirainvest_com.schemas.schema import PostsModel


router = APIRouter(prefix="/post", tags=["Post"])


# ALL PLATFORM POSTS GENERATED VIA DATA IMPORTS


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


@router.post("/upload/post_photos", status_code=status.HTTP_200_OK, response_model=PostsModel)
async def upload_post_photos_route(
    post_id: int,
    images: List[UploadFile] = File(...),
    token=Depends(auth_depends_user_id),
):
    photo_urls = [
        upload_post_photo_controller(
            image.file.read(), image.filename, user_id=token["https://amirainvest.com/user_id"], post_id=post_id
        )
        for image in images
    ]
    post = await get_controller(
        post_id,
    )
    post.photos.extend(photo_urls)
    return (await update_controller(post.__dict__)).dict()
