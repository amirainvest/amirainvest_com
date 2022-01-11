from typing import List

from fastapi import APIRouter, Security

from backend_amirainvest_com.controllers import user_subscriptions
from backend_amirainvest_com.controllers.auth import auth_dep
from common_amirainvest_com.schemas.schema import UserSubscriptionsModel


router = APIRouter(
    prefix="/user_subscriptions",
    tags=["User Subscriptions"],
    dependencies=[Security(auth_dep, scopes=[])],
)


@router.get(
    "/subscriber",
    status_code=200,
    response_model=List[UserSubscriptionsModel],
)
async def get_subscriptions_for_subscriber(subscriber_id):
    subscriptions = await user_subscriptions.get_subscriptions_for_subscriber(subscriber_id)
    subscriptions = [x.__dict__ for x in subscriptions]
    return subscriptions


@router.get(
    "/creator",
    status_code=200,
    response_model=List[UserSubscriptionsModel],
)
async def get_subscriptions_for_creator(creator_id):
    subscriptions = await user_subscriptions.get_subscriptions_for_creator(creator_id)
    subscriptions = [x.__dict__ for x in subscriptions]
    return subscriptions


@router.post("/subscribe", status_code=200, response_model=UserSubscriptionsModel)
async def create_subscription(subscriber_id: str, creator_id: str):
    user_subscription = await user_subscriptions.get_user_subscription(subscriber_id, creator_id)
    if not user_subscription:
        user_subscription = await user_subscriptions.create_user_subscription(subscriber_id, creator_id)
    else:
        user_subscription.is_deleted = False
        user_subscription = await user_subscriptions.update_user_subscription(user_subscription.__dict__)
    user_subscription = user_subscription.__dict__
    return user_subscription


@router.put("/unsubscribe", status_code=200, response_model=UserSubscriptionsModel)
async def unsubscribe(subscriber_id: str, creator_id: str):
    subscription = await user_subscriptions.get_user_subscription(subscriber_id, creator_id)
    subscription.is_deleted = True
    updated_subscription = await user_subscriptions.update_user_subscription(subscription.__dict__)
    return updated_subscription
