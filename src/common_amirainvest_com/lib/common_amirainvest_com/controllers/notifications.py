from sqlalchemy import insert
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.notifications.model import CreateModel
from common_amirainvest_com.schemas.schema import Notifications, NotificationTypes
from common_amirainvest_com.utils.decorators import Session


async def create_notification(user_id: str, notification_type: str, body: dict, redirect: str, picture_url: str):
    await create_controller(
        user_id,
        CreateModel(
            notification_type=NotificationTypes(notification_type),
            body=body,
            redirect=redirect,
            picture_url=picture_url,
        ),
    )


@Session
async def create_controller(session: AsyncSession, user_id: str, create_data: CreateModel) -> Row:
    create_data_dict = create_data.dict(exclude_none=True)
    create_data_dict["user_id"] = user_id
    return (await session.execute(insert(Notifications).values(**create_data_dict).returning(Notifications))).one()
