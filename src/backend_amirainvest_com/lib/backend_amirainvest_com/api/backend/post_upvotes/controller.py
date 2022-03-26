from sqlalchemy import insert, delete
from sqlalchemy.engine import Row

from backend_amirainvest_com.api.backend.post_upvotes.model import UpvoteModel
from common_amirainvest_com.schemas.schema import PostUpvotes
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_upvote(session: AsyncSession, user_id: str, upvote_data: UpvoteModel) -> Row:
    upvote = upvote_data.dict(exclude_none=True)
    return (
        await session.execute(
            insert(PostUpvotes)
            .values({"user_id":user_id, **upvote})
            .returning(PostUpvotes)
        )
    ).one()


@Session
async def create_upvote(session: AsyncSession, user_id: str, post_id: int):
    return (
        await session.execute(
            delete(PostUpvotes)
            .where(PostUpvotes.user_id == user_id)
            .where(PostUpvotes.post_id == post_id)
        )
    )
