from pydantic import BaseModel


class UserSearch(BaseModel):
    name: str
    user_id: str


class ContentSearch(BaseModel):
    text: str
    post_id: int
