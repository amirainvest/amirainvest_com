import datetime

from fastapi import HTTPException, status
from sqlalchemy import delete, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import functions

from backend_amirainvest_com.api.backend.user_route import model
from backend_amirainvest_com.api.backend.user_route.model import SearchableAttributes
from backend_amirainvest_com.controllers.data_imports import add_data_import_data_to_sqs_queue
from backend_amirainvest_com.utils import auth0_utils
from common_amirainvest_com.schemas.schema import Users
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.generic_utils import get_class_attrs


@Session
async def get_controller(session, user_id: str) -> Users:
    return (await session.execute(select(Users).where(Users.id == user_id))).scalars().first()


@Session
async def list_controller(session, list_request: model.ListInputModel):
    query = select(Users)

    for filter_ in list_request.filters:
        if filter_.attribute == SearchableAttributes.full_name:
            column_to_query = functions.concat(Users.first_name, Users.last_name)
        else:
            column_to_query = getattr(Users, filter_.attribute.value)

        if filter_.filter_type == model.FilterTypes.substring_match:
            query = query.filter(column_to_query.ilike(f"%{filter_.value.lower()}%"))

    if list_request.sort is not None:
        if list_request.sort.attribute == SearchableAttributes.full_name:
            column_to_sort = functions.concat(Users.first_name, Users.last_name)
        else:
            column_to_sort = getattr(Users, list_request.sort.attribute.value)
        query = query.order_by(getattr(column_to_sort, list_request.sort.order.value)())

    data = await session.execute(query)
    return data.scalars().all()


@Session
async def update_controller(session, user_id: str, user_data: model.UserUpdate) -> Users:
    user_data_dict = user_data.dict(exclude_none=True)
    if user_data.is_deleted is True:
        user_data_dict["deleted_at"] = datetime.datetime.utcnow()
    elif user_data.is_deleted is False:
        user_data_dict["deleted_at"] = None

    return (
        await (session.execute(update(Users).where(Users.id == user_id).values(**user_data_dict).returning(Users)))
    ).one()


def handle_data_imports(
    creator_id: str,
    expedited: bool,
    substack_username: str = "",
    youtube_channel_id: str = "",
    twitter_username: str = "",
):
    sqs_digestible_platform_data = []
    if substack_username != "":
        sqs_digestible_platform_data.append(
            {"platform": "substack", "unique_platform_id": substack_username, "creator_id": creator_id}
        )
    if youtube_channel_id != "":
        sqs_digestible_platform_data.append(
            {"platform": "youtube", "unique_platform_id": youtube_channel_id, "creator_id": creator_id}
        )
    if twitter_username != "":
        sqs_digestible_platform_data.append(
            {"platform": "twitter", "unique_platform_id": twitter_username, "creator_id": creator_id}
        )
    if sqs_digestible_platform_data:
        add_data_import_data_to_sqs_queue(
            sqs_digestible_platform_data,
            expedited=expedited,
        )


@Session
async def create_user_no_sub(session, user_data: dict) -> Users:
    user = Users(**{k: v for k, v in user_data.items() if k in get_class_attrs(Users)})
    session.add(user)
    return user


async def handle_user_create(user_data: dict):  # depricated
    user = await create_user_no_sub(
        user_data,
    )
    handle_data_imports(
        str(user.id), user_data["substack_username"], user_data["youtube_channel_id"], user_data["twitter_username"]
    )
    return user


@Session
async def create_controller(session: AsyncSession, user_data: model.InitPostModel, sub: str) -> str:
    result = (await session.execute(select(Users.id, Users.email).where(Users.sub == sub))).one_or_none()

    if result is None:
        user = user_data.dict(exclude_none=True)
        user["sub"] = sub
        created_user = (await session.execute(insert(Users).values(**user).returning(Users))).one()

        await session.commit()
        user_id = created_user.id
    else:
        user_id, email = result
        if email != user_data.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=model.Http409Enum.user_sub_missmatch.value.dict(),
            )

    metadata = {"UserId": str(user_id)}
    try:
        await auth0_utils.update_user_app_metadata(sub, metadata)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=model.Http400Enum.auth0_app_metadata_failed.value.dict(),
        )

    return user_id


@Session
async def delete_controller(session: AsyncSession, user_id: str, sub: str):
    await session.execute(delete(Users).where(Users.id == user_id).where(Users.sub == sub))
