from fastapi import APIRouter, Security

from backend_amirainvest_com.controllers import feed
from backend_amirainvest_com.controllers.auth import auth_dep
from backend_amirainvest_com.models.feed import Feed


router = APIRouter(prefix="/feed", tags=["Feed"], dependencies=[Security(auth_dep, scopes=[])])


@router.get("/subscriber/", status_code=200, response_model=Feed)
async def get_subscriber_feed(
    subscriber_id,
    page: int = 0,
):
    posts, feed_type = await feed.get_subscriber_feed(subscriber_id, page)
    return {"posts": posts, "feed_type": feed_type}


@router.get("/creator/", status_code=200, response_model=Feed)
async def get_creator_feed(
    creator_id,
    page: int = 0,
):
    posts, feed_type = await feed.get_creator_feed(creator_id, page)
    return {"posts": posts, "feed_type": feed_type}


@router.get("/discovery/", status_code=200, response_model=Feed)
async def get_discovery_feed(
    user_id: str,
    page: int = 0,
):
    posts = await feed.get_discovery_feed(user_id, page)
    return {"posts": posts, "feed_type": "discovery"}
