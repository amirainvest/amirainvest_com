from typing import Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import NotificationSettingsModel, NotificationsModel, NotificationTypes


assert NotificationsModel
assert NotificationSettingsModel


class CreateModel(BaseModel):
    notification_type: NotificationTypes
    body: dict
    redirect: str
    is_read: Optional[bool]
    is_deleted: Optional[bool]
    picture_url: Optional[str]


class UpdateModel(BaseModel):
    id: int
    is_read: Optional[bool]
    is_deleted: Optional[bool]


class InitReturnSettingsModel(BaseModel):
    id: int


class CreateSettingsModel(BaseModel):
    mention: Optional[bool]
    upvote: Optional[bool]
    shared_change: Optional[bool]
    watchlist_price: Optional[bool]
    shared_price: Optional[bool]
    email_trades: Optional[bool]


class UpdateSettingsModel(BaseModel):
    id: int
    mention: Optional[bool]
    upvote: Optional[bool]
    shared_change: Optional[bool]
    watchlist_price: Optional[bool]
    shared_price: Optional[bool]
    email_trades: Optional[bool]
