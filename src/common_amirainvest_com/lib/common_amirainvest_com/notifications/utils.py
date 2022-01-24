from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.schemas.schema import Notifications, NotificationTypes

@Session
async def create_notification(session):
    return