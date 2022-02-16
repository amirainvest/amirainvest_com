from typing import List

from fastapi import APIRouter, Depends

from backend_amirainvest_com.controllers import user_subscriptions
from backend_amirainvest_com.controllers.auth import auth_depends_user_id
from common_amirainvest_com.schemas.schema import UserSubscriptionsModel


router = APIRouter(prefix="/user_subscriptions", tags=["User Subscriptions"])


@router.get(
    "/subscriber",
    status_code=200,
    response_model=List[UserSubscriptionsModel],
)
async def get_subscriptions_for_subscriber(token=Depends(auth_depends_user_id)):
    subscriber_id = token["https://amirainvest.com/user_id"]
    subscriptions = await user_subscriptions.get_subscriptions_for_subscriber(subscriber_id)
    subscriptions = [x.__dict__ for x in subscriptions]
    return subscriptions


@router.get(
    "/creator",
    status_code=200,
    response_model=List[UserSubscriptionsModel],
)
async def get_subscriptions_for_creator(token=Depends(auth_depends_user_id)):
    creator_id = token["https://amirainvest.com/user_id"]
    subscriptions = await user_subscriptions.get_subscriptions_for_creator(creator_id)
    subscriptions = [x.__dict__ for x in subscriptions]
    return subscriptions


@router.post("/subscribe", status_code=200, response_model=UserSubscriptionsModel)
async def create_subscription(creator_id: str, token=Depends(auth_depends_user_id)):
    subscriber_id = token["https://amirainvest.com/user_id"]
    user_subscription = await user_subscriptions.get_user_subscription(subscriber_id, creator_id)
    if not user_subscription:
        user_subscription = await user_subscriptions.create_user_subscription(subscriber_id, creator_id)
    else:
        user_subscription.is_deleted = False
        user_subscription = await user_subscriptions.update_user_subscription(user_subscription.dict())
    return user_subscription.dict()


@router.put("/unsubscribe", status_code=200, response_model=UserSubscriptionsModel)
async def unsubscribe(creator_id: str, token=Depends(auth_depends_user_id)):
    subscriber_id = token["https://amirainvest.com/user_id"]
    subscription = await user_subscriptions.get_user_subscription(subscriber_id, creator_id)
    subscription.is_deleted = True
    updated_subscription = await user_subscriptions.update_user_subscription(subscription.__dict__)
    return updated_subscription
