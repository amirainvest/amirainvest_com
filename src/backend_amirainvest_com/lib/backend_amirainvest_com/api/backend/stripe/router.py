from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.stripe.controller import create_controller, get_controller
from backend_amirainvest_com.api.backend.stripe.model import StripeModel
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/stripe", tags=["Stripe Integration"])


@router.post(
    "/create", summary="Store Stripe Indentification Record", status_code=status.HTTP_200_OK, response_model=StripeModel
)
async def create_route(stripe_id: str, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    model = await create_controller(user_id, stripe_id)
    return StripeModel(stripe_id=model.stripe_id)


@router.post(
    "/get",
    summary="Retriever Stripe Indentification Record",
    status_code=status.HTTP_200_OK,
    response_model=StripeModel,
)
async def get_route(token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    model = await get_controller(user_id)
    return StripeModel(stripe_id=model.stripe_id)
