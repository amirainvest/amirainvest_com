from fastapi import APIRouter, Depends, Response

from backend_amirainvest_com.controllers import search
from backend_amirainvest_com.controllers.auth import auth_required, token_auth_scheme


router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/recent_content", status_code=200)
@auth_required
async def search_content(response: Response, token: str = Depends(token_auth_scheme)):
    data = await search.get_all_recent_content()
    return data


@router.get("/users", status_code=200)
@auth_required
async def search_users(response: Response, token: str = Depends(token_auth_scheme)):
    data = await search.get_all_users()
    return data


@router.get("/search_content", status_code=200)
@auth_required
async def get_like_content(search_term, response: Response, token: str = Depends(token_auth_scheme)):
    data = await search.get_like_content(search_term=search_term)
    return data


@router.get("/search_creators", status_code=200)
@auth_required
async def get_like_creator(search_term, response: Response, token: str = Depends(token_auth_scheme)):
    data = await search.get_like_creator(search_term=search_term)
    return data
