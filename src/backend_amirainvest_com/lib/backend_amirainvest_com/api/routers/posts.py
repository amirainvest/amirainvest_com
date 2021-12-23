from fastapi import APIRouter, Depends

from backend_amirainvest_com.controllers import posts
from backend_amirainvest_com.controllers.auth import auth_required, token_auth_scheme
from common_amirainvest_com.schemas.schema import PostsModel


router = APIRouter(prefix="/amira_posts", tags=["Amira Posts"])


# ALL PLATFORM POSTS GENERATED VIA DATA IMPORTS


@router.post("/", status_code=201, response_model=PostsModel)
@auth_required
async def create_amira_post(post_data: PostsModel, token: str = Depends(token_auth_scheme)):
    data = await posts.create_amira_post(post_data.dict())
    return 201, data


@router.put("/", status_code=201, response_model=PostsModel)
@auth_required
async def update_post(post_data: PostsModel, token: str = Depends(token_auth_scheme)):
    data = await posts.update_amira_post(post_data.dict())
    return 201, data
