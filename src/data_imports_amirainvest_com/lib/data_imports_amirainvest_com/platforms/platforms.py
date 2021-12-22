from abc import ABC, abstractmethod

from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import SubstackUsers, TwitterUsers, YouTubers
from common_amirainvest_com.utils.decorators import Session


PLATFORM_MAP = {
    "twitter": {"class": TwitterUsers, "platform_unique_id_name": "twitter_user_id"},
    "youtube": {"class": YouTubers, "platform_unique_id_name": "channel_id"},
    "substack": {"class": SubstackUsers, "platform_unique_id_name": "username"},
}


class PlatformUser(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_unique_id(self):
        pass

    @staticmethod
    @Session
    async def get_user_platform_pair_exists(session, platform, platform_unique_id):
        results = await session.execute(
            select(PLATFORM_MAP[platform]["class"]).filter_by(
                **{PLATFORM_MAP[platform]["platform_unique_id_name"]: platform_unique_id}
            )
        )
        return True if results.all() else False
