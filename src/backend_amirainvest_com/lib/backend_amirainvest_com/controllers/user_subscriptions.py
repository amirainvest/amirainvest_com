import datetime
import uuid

from sqlalchemy import delete
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import UserSubscriptions
from common_amirainvest_com.utils.database_utils import update
from common_amirainvest_com.utils.decorators import Session


async def update_user_subscription(user_subscription_data: dict):
    subscription = await update(UserSubscriptions, user_subscription_data)
    return subscription


@Session
async def create_user_subscription(session, subscriber_id: uuid.UUID, creator_id: uuid.UUID):
    subscription = UserSubscriptions(
        creator_id=creator_id,
        subscriber_id=subscriber_id,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
        is_deleted=False,
    )
    session.add(subscription)
    return subscription


@Session
async def get_subscriptions_for_subscriber(session, subscriber_id: str):
    data = await session.execute(select(UserSubscriptions).where(UserSubscriptions.subscriber_id == subscriber_id))
    return data.scalars().all()


@Session
async def get_subscriptions_for_creator(session, creator_id):
    data = await session.execute(select(UserSubscriptions).where(UserSubscriptions.creator_id == creator_id))
    return data.scalars().all()


@Session
async def get_user_subscription(session, subscriber_id: str, creator_id: str):
    data = await session.execute(
        select(UserSubscriptions)
        .where(UserSubscriptions.subscriber_id == subscriber_id)
        .where(UserSubscriptions.creator_id == creator_id)
    )
    return data.scalars().first()


@Session
async def delete_user_subscription(session, subscriber_id: str, creator_id: str):
    await session.execute(
        delete(UserSubscriptions)
        .where(UserSubscriptions.subscriber_id == subscriber_id)
        .where(UserSubscriptions.creator_id == creator_id)
    )
