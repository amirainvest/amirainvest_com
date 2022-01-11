from fastapi import APIRouter, Security

from backend_amirainvest_com.controllers import posts
from backend_amirainvest_com.controllers.auth import auth_dep
from backend_amirainvest_com.models.post import PostCreate
from common_amirainvest_com.schemas.schema import PostsModel


router = APIRouter(prefix="/amira_posts", tags=["Amira Posts"], dependencies=[Security(auth_dep, scopes=[])])


# ALL PLATFORM POSTS GENERATED VIA DATA IMPORTS


@router.post("", status_code=200, response_model=PostsModel)
async def create_amira_post(post_data: PostCreate):
    data = await posts.create_amira_post(post_data.dict())
    data = data.__dict__
    return data


@router.put("", status_code=200, response_model=PostsModel)
async def update_amira_post(post_data: PostsModel):
    data = await posts.update_amira_post(post_data.dict())
    data = data.__dict__
    return data
