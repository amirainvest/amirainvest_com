import uuid
from typing import List

from fastapi import APIRouter, File, Security, status, UploadFile

from backend_amirainvest_com.api.backend.post_route.controller import (
    create_controller,
    get_controller,
    update_controller,
    upload_post_photo_controller,
)
from backend_amirainvest_com.api.backend.post_route.model import CreateModel, GetModel, UpdateModel
from backend_amirainvest_com.controllers.auth import auth_dep


router = APIRouter(prefix="/post", tags=["Post"], dependencies=[Security(auth_dep, scopes=[])])


# ALL PLATFORM POSTS GENERATED VIA DATA IMPORTS


@router.post("/create", status_code=status.HTTP_200_OK, response_model=GetModel)
async def create_route(user_id: uuid.UUID, post_data: CreateModel):
    return (
        await create_controller(
            user_id,
            post_data,
        )
    )._asdict()


@router.post("/update", status_code=status.HTTP_200_OK, response_model=GetModel)
async def update_route(user_id: uuid.UUID, post_data: UpdateModel):
    return (
        await update_controller(
            user_id,
            post_data,
        )
    )._asdict()


@router.post("/upload/post_photos", status_code=status.HTTP_200_OK, response_model=GetModel)
async def upload_post_photos_route(post_id: int, user_id: str, images: List[UploadFile] = File(...)):
    photo_urls = [upload_post_photo_controller(image.file.read(), image.filename, user_id, post_id) for image in images]
    post = await get_controller(
        post_id,
    )
    post.photos.extend(photo_urls)
    return (await update_controller(post.__dict__)).dict()
