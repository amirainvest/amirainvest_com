from fastapi import APIRouter, Security

from backend_amirainvest_com.api.backend.bookmark.controller import (
    create_controller,
    delete_controller,
    get_all_for_user_controller,
)
from backend_amirainvest_com.api.backend.bookmark.model import CreateModel, GetModel, ListModel
from backend_amirainvest_com.controllers.auth import auth_dep


router = APIRouter(prefix="/bookmark", tags=["Bookmark"], dependencies=[Security(auth_dep, scopes=[])])


@router.post("/list", status_code=200, response_model=ListModel)
async def list_route(
    user_id: str,
):
    user_bookmarks = await get_all_for_user_controller(user_id)
    user_bookmarks = [x.dict() for x in user_bookmarks]
    return {"results": user_bookmarks}


@router.post("/create", status_code=201, response_model=GetModel)
async def create_route(
    user_id: str,
    bookmark_data: CreateModel,
):
    bookmark = await create_controller(user_id, bookmark_data.dict())
    bookmark = bookmark.dict()
    return bookmark


@router.post("/delete", status_code=200)
async def delete_route(
    user_id: str,
    bookmark_id: int,
):
    await delete_controller(bookmark_id, user_id)
    return 200
