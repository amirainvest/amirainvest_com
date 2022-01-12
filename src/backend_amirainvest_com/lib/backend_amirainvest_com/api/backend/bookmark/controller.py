import typing as t

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import aliased

from common_amirainvest_com.schemas.schema import Bookmarks
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_all_for_user_controller(session: AsyncSession, user_id: str) -> t.List[Bookmarks]:
    data = await session.execute(select(aliased(Bookmarks)).where(Bookmarks.user_id == user_id))
    return data.scalars().all()


@Session
async def create_controller(session: AsyncSession, user_id: str, bookmark_data: dict) -> Bookmarks:
    bookmark_data["user_id"] = user_id
    bookmark = Bookmarks(**bookmark_data)
    session.add(bookmark)
    return bookmark


@Session
async def delete_controller(session: AsyncSession, bookmark_id: int, user_id: str):
    await session.execute(delete(Bookmarks).where(Bookmarks.id == bookmark_id, Bookmarks.user_id == user_id))
