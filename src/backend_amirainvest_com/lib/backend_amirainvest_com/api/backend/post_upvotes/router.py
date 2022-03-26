from fastapi import APIRouter, Depends, HTTPException, status

from backend_amirainvest_com.api.backend.post_upvotes.controller import create_upvote
from backend_amirainvest_com.api.backend.post_upvotes.model import UpvoteModel
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix='/posts/upvotes', tage=["Post Upvotes"])

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=UpvoteModel,
    response_model_exclude_none=True
)
async def create_upvote(upvote_data: UpvoteModel, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    return await create_upvote(user_id, upvote_data)


@router.post("/delete", status_code=status.HTTP_200_OK)
async def delete_upvote(upvote_data: UpvoteModel, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    return await delete_upvote(user_id, upvote_data)