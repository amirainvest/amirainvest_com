from common_amirainvest_com.schemas.schema import SubstackUsers
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_youtuber(session, substack_user_data: dict):
    substack_user = SubstackUsers(**substack_user_data)
    session.add(substack_user)
    return substack_user
