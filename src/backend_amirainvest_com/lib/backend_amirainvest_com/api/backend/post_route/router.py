from typing import List

from fastapi import APIRouter, Depends, File, status, UploadFile

from backend_amirainvest_com.api.backend.post_route.controller import (
    create_controller,
    get_controller,
    list_controller,
    PAGE_SIZE,
    update_controller,
    upload_post_photo_controller,
)
from backend_amirainvest_com.api.backend.post_route.model import (
    CreateModel,
    GetModel,
    ListInputModel,
    ListReturnModel,
    UpdateModel,
)
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/post", tags=["Post"])


# ALL PLATFORM POSTS GENERATED VIA DATA IMPORTS


@router.post("/list", status_code=status.HTTP_200_OK, response_model=ListReturnModel)
async def list_route(
    feed_wanted: ListInputModel,
    page_size: int = PAGE_SIZE,
    last_loaded_post_id: int = 0,
    token=Depends(auth_depends_user_id),
):
    return_feed, return_feed_type = await list_controller(
        feed_wanted=feed_wanted,
        subscriber_id=token["https://amirainvest.com/user_id"],
        page_size=page_size,
        last_loaded_post_id=last_loaded_post_id,
    )
    return ListReturnModel(posts=return_feed, feed_type=return_feed_type)


@router.post("/create", status_code=status.HTTP_200_OK, response_model=GetModel)
async def create_route(
    user_id: str,
    post_data: CreateModel,
    token=Depends(auth_depends_user_id),
):
    return (
        await create_controller(
            user_id,
            post_data,
        )
    )._asdict()


@router.post("/update", status_code=status.HTTP_200_OK, response_model=GetModel)
async def update_route(
    user_id: str,
    post_data: UpdateModel,
    token=Depends(auth_depends_user_id),
):
    return (
        await update_controller(
            user_id,
            post_data,
        )
    )._asdict()


@router.post("/upload/post_photos", status_code=status.HTTP_200_OK, response_model=GetModel)
async def upload_post_photos_route(
    post_id: int,
    user_id: str,
    images: List[UploadFile] = File(...),
    token=Depends(auth_depends_user_id),
):
    photo_urls = [upload_post_photo_controller(image.file.read(), image.filename, user_id, post_id) for image in images]
    post = await get_controller(
        post_id,
    )
    post.photos.extend(photo_urls)
    return (await update_controller(post.__dict__)).dict()
