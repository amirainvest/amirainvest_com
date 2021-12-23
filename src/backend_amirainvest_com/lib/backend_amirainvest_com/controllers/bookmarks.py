from sqlalchemy import delete, select

from common_amirainvest_com.schemas.schema import Bookmarks
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_all_user_bookmarks(session, user_id):
    data = await session.execute(select(Bookmarks).where(Bookmarks.user_id == user_id))
    return data.scalars().all()


@Session
async def create_bookmark(session, bookmark_data: dict):
    bookmark = Bookmarks(**bookmark_data)
    session.add(bookmark)
    return bookmark


@Session
async def delete_bookmark(session, bookmark_id):
    await session.execute(delete(Bookmarks).where(Bookmarks.id == bookmark_id))
