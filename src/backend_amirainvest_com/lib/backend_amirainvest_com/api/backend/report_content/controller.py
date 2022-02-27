from sqlalchemy import insert
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from backend_amirainvest_com.api.backend.report_content.model import ReportPostModel
from common_amirainvest_com.schemas.schema import PostReports
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_controller(session: AsyncSession, user_id: str, post_id: int) -> Row:
    return (
        await session.execute(
            insert(PostReports).values({"user_id": user_id, "post_id": post_id}).returning(PostReports)
        )
    ).one()
