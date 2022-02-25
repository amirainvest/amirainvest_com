from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.stripe.controller import (
    get_controller,
    create_controller
)
from backend_amirainvest_com.api.backend.stripe.model import StripeModel
from backend_amirainvest_com.controllers.auth import auth_depends_user_id

router = APIRouter(prefix="/stripe", tags=["Stripe Integration"])


@router.post(
    "/create",
    summary="Store Stripe Indentification Record",
    status_code=status.HTTP_200_OK,
    response_model=StripeModel
    )
async def create_route(stripe_id: str, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    return create_controller(user_id, stripe_id)


@router.post(
    "/get",
    summary="Retriever Stripe Indentification Record",
    status_code=status.HTTP_200_OK,
    response_model=StripeModel
    )
async def get_route(token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    return get_controller(user_id)
