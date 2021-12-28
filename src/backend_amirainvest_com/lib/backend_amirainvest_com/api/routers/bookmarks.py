from typing import List

from fastapi import APIRouter, Security

from backend_amirainvest_com.controllers import bookmarks
from backend_amirainvest_com.controllers.auth import auth_dep
from backend_amirainvest_com.models.bookmark import BookmarkCreate
from common_amirainvest_com.schemas.schema import BookmarksModel


router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"], dependencies=[Security(auth_dep, scopes=[])])


@router.get("/", status_code=200, response_model=List[BookmarksModel])
async def get_all_user_bookmarks(
    user_id: str,
):
    user_bookmarks = await bookmarks.get_all_user_bookmarks(user_id)
    user_bookmarks = [x.__dict__ for x in user_bookmarks]
    return user_bookmarks


@router.post("/", status_code=201, response_model=BookmarksModel)
async def create_bookmark(
    bookmark_data: BookmarkCreate,
):
    bookmark = await bookmarks.create_bookmark(bookmark_data.dict())
    bookmark = bookmark.__dict__
    return bookmark


@router.delete("/", status_code=200)
async def delete_bookmark(
    bookmark_id: int,
):
    await bookmarks.delete_bookmark(bookmark_id)
    return 200
