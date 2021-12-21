from common_amirainvest_com.schemas.schema import SubstackUsers
from common_amirainvest_com.utils.decorators import Session
from common_amirainvest_com.utils.pydantic_utils import sqlalchemy_to_pydantic


substack_users_pydantic_model = sqlalchemy_to_pydantic(SubstackUsers)


@Session
async def create_youtuber(session, substack_user_data: dict):
    substack_user = SubstackUsers(**substack_user_data)
    session.add(substack_user)
    return substack_user
