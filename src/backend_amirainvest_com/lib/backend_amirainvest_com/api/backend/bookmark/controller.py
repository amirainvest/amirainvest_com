import typing as t

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_amirainvest_com.api.backend.bookmark.model import CreateModel
from common_amirainvest_com.schemas.schema import Bookmarks
from common_amirainvest_com.utils.decorators import Session


@Session
async def list_controller(session: AsyncSession, user_id: str) -> t.List[Bookmarks]:
    data = await session.execute(
        select(Bookmarks)
        .where(Bookmarks.user_id == user_id)
        .where(Bookmarks.is_deleted.is_(False))
    )
    return data.scalars().all()


@Session
async def create_controller(session: AsyncSession, user_id: str, bookmark_data: CreateModel) -> Bookmarks:
    response = await recreate_bookmark(user_id, bookmark_data)
    if response:
        return response
    bookmark_data_dict = bookmark_data.dict(exclude_none=True)
    bookmark_data_dict["user_id"] = user_id
    bookmark = Bookmarks(**bookmark_data_dict)
    session.add(bookmark)
    return bookmark


@Session
async def recreate_bookmark(session: AsyncSession, user_id: str, bookmark_data: CreateModel)-> Bookmarks:
    session.execute(
        update(Bookmarks)
        .where(Bookmarks.user_id == user_id)
        .where(Bookmarks.post_id == bookmark_data.post_id)
        .values({"is_deleted":False})
        .returning(Bookmarks)
    ).one_or_none()


@Session
async def delete_controller(session: AsyncSession, user_id: str, bookmark_id: int):
    await session.execute(
        update(Bookmarks)
        .where(Bookmarks.id == bookmark_id, Bookmarks.user_id == user_id)
        .values({"is_deleted":True})
    )
