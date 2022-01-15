import uuid

from sqlalchemy import insert, update
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.backend.post_route.model import CreateModel, UpdateModel
from backend_amirainvest_com.utils.s3 import S3
from common_amirainvest_com.s3.consts import AMIRA_POST_PHOTOS_S3_BUCKET
from common_amirainvest_com.schemas.schema import Posts
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_controller(session: AsyncSession, post_id: int):
    return (await session.execute(select(Posts).where(Posts.id == post_id))).scalars().first()


@Session
async def update_controller(session: AsyncSession, user_id: uuid.UUID, update_data: UpdateModel) -> Row:
    return (
        await (
            session.execute(
                update(Posts)
                    .where(Posts.creator_id == user_id)
                    .where(Posts.id == update_data.id)
                    .values(**update_data.dict(exclude_none=True))
                    .returning(Posts)
            )
        )
    ).one()


@Session
async def create_controller(session: AsyncSession, user_id: uuid.UUID, create_data: CreateModel) -> Row:
    create_data_dict = create_data.dict(exclude_none=True)
    create_data_dict["creator_id"] = user_id
    return (await session.execute(insert(Posts).values(**create_data_dict).returning(Posts))).one()


def upload_post_photo_controller(file_bytes: bytes, filename: str, user_id: str, post_id: int):
    return S3().upload_file_by_bytes(file_bytes, f"{user_id}/{post_id}/{filename}", AMIRA_POST_PHOTOS_S3_BUCKET)
