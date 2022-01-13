from typing import List

from fastapi import APIRouter, Security

from backend_amirainvest_com.controllers import search
from backend_amirainvest_com.controllers.auth import auth_dep
from backend_amirainvest_com.models.search import ContentSearch, UserSearch


router = APIRouter(prefix="/search", tags=["Search"], dependencies=[Security(auth_dep, scopes=[])])


@router.get("/recent_content", status_code=200, response_model=List[ContentSearch])
async def search_recent_content():
    data = await search.get_all_recent_content()
    return [{"text": x.text, "post_id": x.id} for x in data]


@router.get("/content", status_code=200, response_model=List[ContentSearch])
async def get_like_content(search_term: str):
    data = await search.get_like_content(search_term=search_term)
    return [{"text": x.text, "post_id": x.id} for x in data]


@router.get("/users", status_code=200, response_model=List[UserSearch])
async def search_users():
    all_users = await search.get_all_users()
    return [
        {
            "name": user.name,
            "user_id": user.id,
            "benchmark": user.benchmark,
            "chip_labels": user.chip_labels
        } for user in all_users
    ]


@router.get("/creators", status_code=200, response_model=List[UserSearch])
async def get_like_creator(search_term: str):
    matching_users = await search.get_like_creator(search_term=search_term)
    return [
        {
            "name": user.name,
            "user_id": user.id,
            "benchmark": user.benchmark,
            "chip_labels": user.chip_labels
        } for user in matching_users
    ]
