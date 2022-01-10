from sqlalchemy.future import select
from sqlalchemy import update

from backend_amirainvest_com.controllers.data_imports import add_data_import_data_to_sqs_queue
from common_amirainvest_com.schemas.schema import Users
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.generic_utils import get_class_attrs


@Session
async def get_user(session, user_id: str) -> Users:
    return (await session.execute(select(Users).where(Users.id == user_id))).scalars().first()


@Session
async def create_user(session, user_data: dict) -> Users:
    user = Users(**{k: v for k, v in user_data.items() if k in get_class_attrs(Users)})
    session.add(user)
    return user


@Session
async def update_user(session, user_data: dict) -> Users:
    await (
        session.execute(
            update(Users)
            .where(Users.id == user_data["id"])
            .values(**{k: v for k, v in user_data.items() if k in Users.__dict__ and v is not None})
        )
    )
    return (await session.execute(select(Users).where(Users.id == user_data["id"]))).scalars().first()


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


async def handle_user_create(user_data: dict):
    user = await create_user(user_data)
    handle_data_imports(
        str(user.id), user_data["substack_username"], user_data["youtube_channel_id"], user_data["twitter_username"]
    )
    return user
