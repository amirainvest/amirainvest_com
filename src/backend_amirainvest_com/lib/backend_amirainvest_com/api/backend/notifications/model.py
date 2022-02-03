import uuid
from typing import List, Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import NotificationsModel, NotificationSettingsModel, NotificationTypes


assert NotificationsModel
assert NotificationSettingsModel

class CreateModel(NotificationsModel):
    notification_type: NotificationTypes
    text : str
    redirect_id : str
    mark_as_read: Optional[bool]
    is_deleted : Optional[bool]

class UpdateModel(CreateModel):
    id: int
    mark_as_read: Optional[bool]
    is_deleted : Optional[bool]

class InitReturnSettingsModel(BaseModel):
    id: int

class CreateSettingsModel(BaseModel):
    mention: Optional[bool]
    upvotes: Optional[bool]
    shared_change: Optional[bool]
    watchlist_price: Optional[bool]
    shared_price: Optional[bool]
    email_trades: Optional[bool]

class UpdateSettingsModel(BaseModel):
    id: int
    mention: Optional[bool]
    upvotes: Optional[bool]
    shared_change: Optional[bool]
    watchlist_price: Optional[bool]
    shared_price: Optional[bool]
    email_trades: Optional[bool]
