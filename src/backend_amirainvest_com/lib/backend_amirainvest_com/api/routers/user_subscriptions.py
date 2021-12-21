from typing import List

from fastapi import APIRouter, Depends

from backend_amirainvest_com.controllers import user_subscriptions
from backend_amirainvest_com.controllers.auth import auth_required, token_auth_scheme


router = APIRouter(prefix="/user_subscriptions", tags=["User Subscriptions"])


@router.get(
    "/subscriptions/subscriber/",
    status_code=200,
    response_model=List[user_subscriptions.user_subscriptions_pydantic_model],
)
@auth_required
async def get_subscriptions_for_subscriber(subscriber_id, token: str = Depends(token_auth_scheme)):
    subscriptions = await user_subscriptions.get_subscriptions_for_subscriber(subscriber_id)
    subscriptions = [x.__dict__ for x in subscriptions]
    return subscriptions


@router.get(
    "/subscriptions/creator/",
    status_code=200,
    response_model=List[user_subscriptions.user_subscriptions_pydantic_model],
)
@auth_required
async def get_subscriptions_for_creator(creator_id, token: str = Depends(token_auth_scheme)):
    subscriptions = await user_subscriptions.get_subscriptions_for_creator(creator_id)
    subscriptions = [x.__dict__ for x in subscriptions]
    return subscriptions


@router.post("/subscribe", status_code=200, response_model=user_subscriptions.user_subscriptions_pydantic_model)
@auth_required
async def create_subscription(subscriber_id: str, creator_id: str, token: str = Depends(token_auth_scheme)):
    user_subscription = await user_subscriptions.get_user_subscription(subscriber_id, creator_id)
    if not user_subscription:
        user_subscription = await user_subscriptions.create_user_subscription(subscriber_id, creator_id)
    else:
        user_subscription.is_deleted = False
        await user_subscriptions.update_user_subscription(user_subscription.__dict__)
    return user_subscription


@router.put("/unsubscribe", status_code=200, response_model=user_subscriptions.user_subscriptions_pydantic_model)
@auth_required
async def unsubscribe(subscriber_id: str, creator_id: str, token: str = Depends(token_auth_scheme)):
    subscription = await user_subscriptions.get_user_subscription(subscriber_id, creator_id)
    subscription.is_deleted = True
    updated_subscription = await user_subscriptions.update_user_subscription(subscription.__dict__)
    return updated_subscription
