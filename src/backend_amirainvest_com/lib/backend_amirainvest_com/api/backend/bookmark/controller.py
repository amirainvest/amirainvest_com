import typing as t
import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.backend.bookmark.model import CreateModel
from common_amirainvest_com.schemas.schema import Bookmarks
from common_amirainvest_com.utils.decorators import Session


@Session
async def list_controller(session: AsyncSession, user_id: uuid.UUID) -> t.List[Bookmarks]:
    data = await session.execute(select(Bookmarks).where(Bookmarks.user_id == user_id))
    return data.scalars().all()


@Session
async def create_controller(session: AsyncSession, user_id: uuid.UUID, bookmark_data: CreateModel) -> Bookmarks:
    bookmark_data_dict = bookmark_data.dict(exclude_none=True)
    bookmark_data_dict["user_id"] = user_id
    bookmark = Bookmarks(**bookmark_data_dict)
    session.add(bookmark)
    return bookmark


@Session
async def delete_controller(session: AsyncSession, user_id: uuid.UUID, bookmark_id: int):
    await session.execute(delete(Bookmarks).where(Bookmarks.id == bookmark_id, Bookmarks.user_id == user_id))
