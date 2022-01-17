import datetime
import uuid

from sqlalchemy import insert, update
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.backend.user_route.model import InitPostModel, UserUpdate
from backend_amirainvest_com.controllers.data_imports import add_data_import_data_to_sqs_queue
from common_amirainvest_com.schemas.schema import Users
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.generic_utils import get_class_attrs


@Session
async def get_controller(session, user_id: str) -> Users:
    return (await session.execute(select(Users).where(Users.id == user_id))).scalars().first()


@Session
async def update_controller(session, user_id: str, user_data: UserUpdate) -> Row:
    user_data_dict = user_data.dict(exclude_none=True)
    if user_data.is_deleted is True:
        user_data_dict["deleted_at"] = datetime.datetime.utcnow()
    elif user_data.is_deleted is False:
        user_data_dict["deleted_at"] = None

    return (
        await (session.execute(update(Users).where(Users.id == user_id).values(**user_data_dict).returning(Users)))
    ).one()


def handle_data_imports(creator_id: str, substack_username: str, youtube_channel_id: str, twitter_username: str):
    sqs_digestible_platform_data = []
    if substack_username:
        sqs_digestible_platform_data.append(
            {"platform": "substack", "unique_platform_id": substack_username, "creator_id": creator_id}
        )
    if youtube_channel_id:
        sqs_digestible_platform_data.append(
            {"platform": "youtube", "unique_platform_id": youtube_channel_id, "creator_id": creator_id}
        )
    if twitter_username:
        sqs_digestible_platform_data.append(
            {"platform": "twitter", "unique_platform_id": twitter_username, "creator_id": creator_id}
        )
    if sqs_digestible_platform_data:
        add_data_import_data_to_sqs_queue(
            sqs_digestible_platform_data,
            expedited=True,
        )


@Session
async def create_user_no_sub(session, user_data: dict) -> Users:
    user = Users(**{k: v for k, v in user_data.items() if k in get_class_attrs(Users)})
    session.add(user)
    return user


async def handle_user_create(user_data: dict):
    user = await create_user_no_sub(
        user_data,
    )
    handle_data_imports(
        str(user.id), user_data["substack_username"], user_data["youtube_channel_id"], user_data["twitter_username"]
    )
    return user


@Session
async def create_controller(session: AsyncSession, user_data: InitPostModel, sub: str) -> uuid.UUID:
    user_id = (await session.execute(select(Users.id).where(Users.sub == sub))).scalars().one_or_none()
    if user_id is None:
        user = user_data.dict(exclude_none=True)
        user["sub"] = sub
        created_user = (await session.execute(insert(Users).values(**user).returning(Users))).one()
        user_id = created_user.id

    return user_id
