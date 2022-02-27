from sqlalchemy import delete, insert
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.backend.stripe.model import StripeModel
from common_amirainvest_com.schemas.schema import StripeIdentifiers
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_controller(session: AsyncSession, user_id: str, stripe_id: str) -> Row:
    return (
        await session.execute(
            insert(StripeIdentifiers).values({"user_id": user_id, "stripe_id": stripe_id}).returning(StripeIdentifiers)
        )
    ).one()


@Session
async def get_controller(session: AsyncSession, user_id: str) -> Row:
    return (
        (await session.execute(select(StripeIdentifiers).where(StripeIdentifiers.user_id == user_id))).scalars().one()
    )
