from typing import List, Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import NotificationsModel as GetModel
from common_amirainvest_com.schemas.schema import NotificationSettingsModel as GetSettingsModel


assert GetModel
assert GetSettingsModel

class CreateModel(BaseModel):
    notification_type: str  #from Enum defined in schamas
    text : str
    redirect_id : str
    mark_as_read: Optional[bool]
    is_deleted : Optional[bool]

class UpdateModel(CreateModel):
    id: int
    mark_as_read: Optional[bool]
    is_deleted : Optional[bool]

class CreateSettingsModel(GetSettingsModel):
    mention: Optional[bool]
    upvotes: Optional[bool]
    shared_change: Optional[bool]
    watchlist_price: Optional[bool]
    shared_price: Optional[bool]
    email_trades: Optional[bool]

class UpdateSettingsModel(CreateSettingsModel):
    id: int
    mention: Optional[bool]
    upvotes: Optional[bool]
    shared_change: Optional[bool]
    watchlist_price: Optional[bool]
    shared_price: Optional[bool]
    email_trades: Optional[bool]
