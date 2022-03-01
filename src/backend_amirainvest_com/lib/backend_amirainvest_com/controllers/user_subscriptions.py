import datetime

from sqlalchemy import delete, update
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import SubscriptionLevel, UserSubscriptions, Users
from common_amirainvest_com.utils.decorators import Session


@Session
async def update_user_subscription(session, user_subscription_data: dict):
    await session.execute(
        update(UserSubscriptions)
        .where(UserSubscriptions.id == user_subscription_data["id"])
        .values(**{k: v for k, v in user_subscription_data.items() if k in UserSubscriptions.__dict__})
    )
    return (
        (await session.execute(select(UserSubscriptions).where(UserSubscriptions.id == user_subscription_data["id"])))
        .scalars()
        .first()
    )


@Session
async def create_user_subscription(session, subscriber_id: str, creator_id: str):
    subscription = UserSubscriptions(
        creator_id=creator_id,
        subscriber_id=subscriber_id,
        subscription_level=SubscriptionLevel.standard,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
        is_deleted=False,
    )
    session.add(subscription)
    return subscription


@Session
async def get_subscriptions_for_subscriber(session, subscriber_id: str):
    data = await session.execute(
        select(UserSubscriptions)
        .join(Users)
        .where(UserSubscriptions.subscriber_id == subscriber_id)
        .where(Users.is_deleted.is_(False))
        .where(Users.is_deactivated.is_(False))
    )
    return data.scalars().all()


@Session
async def get_subscriptions_for_creator(session, creator_id):
    data = await session.execute(
        select(UserSubscriptions)
        .join(Users)
        .where(UserSubscriptions.creator_id == creator_id)
        .where(Users.is_deleted.is_(False))
        .where(Users.is_deactivated.is_(False))
    )
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
