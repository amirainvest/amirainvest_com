import uuid

from sqlalchemy import insert, update
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.backend.notifications.model import (
    CreateModel,
    CreateSettingsModel,
    UpdateModel,
    UpdateSettingsModel,
)
from common_amirainvest_com.schemas.schema import Notifications, NotificationSettings, NotificationTypes
from common_amirainvest_com.utils.decorators import Session


# notifications controllers
@Session
async def list_controller(session: AsyncSession, user_id: uuid.UUID):
    return (
        (
            await session.execute(
                select(Notifications).where(Notifications.user_id == user_id).where(Notifications.is_deleted == False)
            )
        )
        .scalars()
        .all()
    )


@Session
async def update_controller(session: AsyncSession, user_id: uuid.UUID, update_data: UpdateModel) -> Row:
    return (
        await (
            session.execute(
                update(Notifications)
                .where(Notifications.user_id == user_id)
                .where(Notifications.id == update_data.id)
                .values(**update_data.dict(exclude_none=True))
                .returning(Notifications)
            )
        )
    ).one()


# @Session
# async def create_controller(session: AsyncSession, user_id: uuid.UUID, create_data: CreateModel) -> Row:
#     create_data_dict = create_data.dict(exclude_none=True)
#     create_data_dict["user_id"] = user_id
#     return (
#         await session.execute(
#             insert(Notifications)
#             .values(**create_data_dict)
#             .returning(Notifications)
#         )
#     ).one()


# notification settings controllers


@Session
async def get_settings_controller(session: AsyncSession, user_id: uuid.UUID):
    return (
        (await (session.execute(select(NotificationSettings).where(NotificationSettings.user_id == user_id))))
        .scalars()
        .one()
    )


@Session
async def update_settings_controller(
    session: AsyncSession, user_id: uuid.UUID, update_data: UpdateSettingsModel
) -> Row:
    return (
        await (
            session.execute(
                update(NotificationSettings)
                .where(NotificationSettings.user_id == user_id)
                .where(NotificationSettings.id == update_data.id)
                .values(**update_data.dict(exclude_none=True))
                .returning(NotificationSettings)
            )
        )
    ).one()


@Session
async def create_settings_controller(
    session: AsyncSession, user_id: uuid.UUID, create_data: CreateSettingsModel
) -> Row:
    result = (
        await session.execute(select(NotificationSettings.id).where(NotificationSettings.user_id == user_id))
    ).one_or_none()

    if result is None:
        create_data_dict = create_data.dict(exclude_none=True)
        create_data_dict["user_id"] = user_id
        created_settings = (
            await session.execute(
                insert(NotificationSettings).values(**create_data_dict).returning(NotificationSettings)
            )
        ).one()
        await session.commit()
        settings_id = created_settings.id

    else:
        (settings_id,) = result

    return settings_id
