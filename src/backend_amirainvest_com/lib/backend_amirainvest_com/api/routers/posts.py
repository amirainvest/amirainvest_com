from typing import List

from fastapi import APIRouter, File, Security, UploadFile

from backend_amirainvest_com.controllers import posts
from backend_amirainvest_com.controllers.auth import auth_dep
from backend_amirainvest_com.controllers.uploads import upload_post_photo
from backend_amirainvest_com.models.post import PostCreate
from common_amirainvest_com.schemas.schema import PostsModel


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
    photo_urls = [upload_post_photo(image.file.read(), image.filename, user_id, post_id) for image in images]
    post = await posts.get_post(post_id)
    post.photos.extend(photo_urls)
    return (await posts.update_post(post.__dict__)).__dict__
