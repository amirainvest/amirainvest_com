import os
from fastapi import APIRouter, File, Security, UploadFile

from backend_amirainvest_com.controllers import posts
from backend_amirainvest_com.controllers.auth import auth_dep
from backend_amirainvest_com.models.post import PostCreate
from backend_amirainvest_com.utils.s3 import build_s3_url
from common_amirainvest_com.schemas.schema import PostsModel
from backend_amirainvest_com.controllers import uploads
from typing import List


router = APIRouter(prefix="/posts", tags=["Posts"], dependencies=[Security(auth_dep, scopes=[])])


# ALL PLATFORM POSTS GENERATED VIA DATA IMPORTS


@router.post("", status_code=200, response_model=PostsModel)
async def create_amira_post(post_data: PostCreate):
    return (await posts.create_post(post_data.dict())).__dict__


@router.put("", status_code=200, response_model=PostsModel)
async def update_amira_post(post_data: PostsModel):
    return (await posts.update_post(post_data.dict())).__dict__


@router.post("/upload_post_photos", status_code=200, response_model=PostsModel)
async def upload_post_photos(post_id: int, user_id: str, images: List[UploadFile] = File(...)):
    # THROW ON QUEUE & 200
    s3_urls = []
    for image in images:
        with open(image.filename, "wb+") as file:
            file.write(image.file.read())
        s3_urls.append(uploads.upload_post_photo(image.filename, user_id, post_id))
        os.remove(image.filename)
    post = await posts.get_post(post_id)
    post.photos.extend(s3_urls)
    return (await posts.update_post(post.__dict__)).__dict__
