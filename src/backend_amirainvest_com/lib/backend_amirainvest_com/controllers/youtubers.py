from common_amirainvest_com.schemas.schema import YouTubers
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.pydantic_utils import sqlalchemy_to_pydantic


youtubers_pydantic_model = sqlalchemy_to_pydantic(YouTubers)


@Session
async def create_youtuber(session, youtuber_data: dict):
    youtuber = YouTubers(**youtuber_data)
    session.add(youtuber)
    return youtuber
