import datetime

from pydantic import BaseModel


class BookmarkCreate(BaseModel):
    user_id: str
    post_id: int
    is_deleted: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
