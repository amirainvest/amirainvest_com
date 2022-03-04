from typing import Optional

from pydantic import BaseModel


class PlaidTokenRequest(BaseModel):
    public_token: str
    is_update: bool


class UpdatePlaidTokenRequest(BaseModel):
    item_id: Optional[str]


class LinkTokenResponse(BaseModel):
    link_token: str


class BadItem(BaseModel):
    user_id: str
    item_id: str
