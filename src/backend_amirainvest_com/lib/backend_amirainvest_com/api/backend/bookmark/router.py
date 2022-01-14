import uuid

from fastapi import APIRouter, Security, status

from backend_amirainvest_com.api.backend.bookmark.controller import (
    create_controller,
    delete_controller,
    list_controller,
)
from backend_amirainvest_com.api.backend.bookmark.model import CreateModel, GetModel, ListModel
from backend_amirainvest_com.controllers.auth import auth_dep


router = APIRouter(prefix="/bookmark", tags=["Bookmark"], dependencies=[Security(auth_dep, scopes=[])])


@router.post("/list", status_code=status.HTTP_200_OK, response_model=ListModel)
async def list_route(
    user_id: uuid.UUID,
):
    user_bookmarks = await list_controller(user_id)
    user_bookmarks = [x.dict() for x in user_bookmarks]
    return {"results": user_bookmarks}


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=GetModel)
async def create_route(
    user_id: uuid.UUID,
    bookmark_data: CreateModel,
):
    bookmark = await create_controller(user_id, bookmark_data)
    bookmark = bookmark.dict()
    return bookmark


@router.post("/delete", status_code=status.HTTP_200_OK)
async def delete_route(
    user_id: uuid.UUID,
    bookmark_id: int,
):
    await delete_controller(user_id, bookmark_id)
    return 200
