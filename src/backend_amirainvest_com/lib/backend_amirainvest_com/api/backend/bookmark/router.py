from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.bookmark.controller import (
    create_controller,
    delete_controller,
    list_controller,
)
from backend_amirainvest_com.api.backend.bookmark.model import CreateModel, GetModel, ListModel
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/bookmark", tags=["Bookmark"])


@router.post("/list", status_code=status.HTTP_200_OK, response_model=ListModel)
async def list_route(token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    user_bookmarks = await list_controller(user_id)
    user_bookmarks = [x.dict() for x in user_bookmarks]
    return {"results": user_bookmarks, "result_count": len(user_bookmarks)}


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=GetModel)
async def create_route(bookmark_data: CreateModel, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    bookmark = await create_controller(user_id, bookmark_data)
    if type(bookmark) is dict:
        return bookmark
    else:
        return bookmark.dict()


@router.post("/delete", status_code=status.HTTP_200_OK)
async def delete_route(bookmark_id: int, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    await delete_controller(user_id, bookmark_id)
    return 200
