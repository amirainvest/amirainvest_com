import datetime
from uuid import UUID

from pydantic import BaseModel


class BookmarkCreate(BaseModel):
    user_id: UUID
    post_id: int
    is_deleted: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
