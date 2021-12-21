from fastapi import APIRouter, Depends

from backend_amirainvest_com.controllers import feed
from backend_amirainvest_com.controllers.auth import auth_required, token_auth_scheme
from backend_amirainvest_com.models.feed import Feed
from common_amirainvest_com.schemas.schema import Posts
from common_amirainvest_com.utils.pydantic_utils import sqlalchemy_to_pydantic


router = APIRouter(prefix="/feed", tags=["Feed"])
post_pydantic_model = sqlalchemy_to_pydantic(Posts)


@router.get("/subscriber/", status_code=200, response_model=Feed)
@auth_required
async def get_subscriber_feed(
    creator_id,
    token: str = Depends(token_auth_scheme),
    page: int = 0,
):
    posts, feed_type = await feed.get_subscriber_feed(creator_id, page)
    return {"posts": posts, "feed_type": feed_type}


@router.get("/creator/", status_code=200, response_model=Feed)
@auth_required
async def get_creator_feed(
    creator_id,
    token: str = Depends(token_auth_scheme),
    page: int = 0,
):
    posts, feed_type = await feed.get_creator_feed(creator_id, page)
    return {"posts": posts, "feed_type": feed_type}


@router.get("/discovery/", status_code=200, response_model=Feed)
@auth_required
async def get_discovery_feed(
    user_id: str,
    token: str = Depends(token_auth_scheme),
    page: int = 0,
):
    posts = await feed.get_discovery_feed(user_id, page)
    return {"posts": posts, "feed_type": "discovery"}
