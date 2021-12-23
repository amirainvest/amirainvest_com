from typing import List

from fastapi import APIRouter, Depends

from backend_amirainvest_com.controllers import bookmarks
from backend_amirainvest_com.controllers.auth import auth_required, token_auth_scheme
from common_amirainvest_com.schemas.schema import BookmarksModel


router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@router.get("/", status_code=200, response_model=List[BookmarksModel])
@auth_required
async def get_all_user_bookmarks(user_id: str, token: str = Depends(token_auth_scheme)):
    user_bookmarks = await bookmarks.get_all_user_bookmarks(user_id)
    user_bookmarks = [x.__dict__ for x in user_bookmarks]
    return user_bookmarks


@router.post("/", status_code=201, response_model=BookmarksModel)
@auth_required
async def create_bookmark(bookmark_data: BookmarksModel, token: str = Depends(token_auth_scheme)):
    bookmark = await bookmarks.create_bookmark(bookmark_data.dict())
    bookmark = bookmark.__dict__
    return bookmark


@router.delete("/", status_code=200)
@auth_required
async def delete_bookmark(bookmark_id: int, token: str = Depends(token_auth_scheme)):
    await bookmarks.delete_bookmark(bookmark_id)
    return 200
