import typing as t
from time import time

from sqlalchemy import insert, update
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

import common_amirainvest_com.utils.query_fragments.feed as qf
from backend_amirainvest_com.api.backend.post_route.model import CreateModel, GetResponseModel, UpdateModel
from backend_amirainvest_com.utils.s3 import S3
from common_amirainvest_com.controllers.notifications import create_notification
from common_amirainvest_com.s3.consts import AMIRA_POST_PHOTOS_S3_BUCKET
from common_amirainvest_com.schemas import schema
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_controller(
    session: AsyncSession, subscriber_id: str, post_id_list: t.List[int]
) -> t.List[GetResponseModel]:
    query = qf.feed_select(subscriber_id=subscriber_id)
    query = query.where(schema.Posts.id.in_(post_id_list))
    data = await session.execute(query)
    posts = [GetResponseModel.from_orm(post) for post in data]
    return posts


@Session
async def update_controller(session: AsyncSession, user_id: str, update_data: UpdateModel) -> Row:
    return (
        await (
            session.execute(
                update(schema.Posts)
                .where(schema.Posts.creator_id == user_id)
                .where(schema.Posts.id == update_data.id)
                .values(**update_data.dict(exclude_none=True))
                .returning(schema.Posts)
            )
        )
    ).one()


@Session
async def create_controller(session: AsyncSession, user_id: str, create_data: CreateModel) -> Row:
    create_data_dict = create_data.dict(exclude_none=True)
    create_data_dict["creator_id"] = user_id
    creator = (await session.execute(select(schema.Users).where(schema.Users.id == user_id))).scalars().one()
    (
        await create_notification(
            user_id,
            "amira_post",
            {"text": f"New Post From {creator.first_name} {creator.last_name}"},
            user_id,
            creator.picture_url,
        )
    )
    return (await session.execute(insert(schema.Posts).values(**create_data_dict).returning(schema.Posts))).one()


def upload_post_photo_controller(file_bytes: bytes, filename: str, user_id: str):
    ext = int(time())
    new_filename = str(ext) + filename
    return S3().upload_file_by_bytes(file_bytes, f"{user_id}/{new_filename}", AMIRA_POST_PHOTOS_S3_BUCKET)
