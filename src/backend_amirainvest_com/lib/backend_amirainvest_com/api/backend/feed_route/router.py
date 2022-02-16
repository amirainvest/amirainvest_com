from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.feed_route.controller import list_controller
from backend_amirainvest_com.api.backend.feed_route.model import ListInputModel, ListReturnModel
from backend_amirainvest_com.controllers.auth import auth_depends_user_id
from common_amirainvest_com.utils.query_fragments.feed import PAGE_SIZE


router = APIRouter(prefix="/feed", tags=["Feed"])


# ALL PLATFORM POSTS GENERATED VIA DATA IMPORTS


@router.post("/get", status_code=status.HTTP_200_OK, response_model=ListReturnModel)
async def list_route(
    feed_info: ListInputModel,
    page_size: int = PAGE_SIZE,
    token=Depends(auth_depends_user_id),
):
    return_feed, return_feed_type = await list_controller(
        feed_info=feed_info,
        subscriber_id=token["https://amirainvest.com/user_id"],
        page_size=page_size,
    )
    return ListReturnModel(posts=return_feed, feed_type=return_feed_type)
