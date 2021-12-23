from common_amirainvest_com.schemas.schema import YouTubers
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_youtuber(session, youtuber_data: dict):
    youtuber = YouTubers(**youtuber_data)
    session.add(youtuber)
    return youtuber
