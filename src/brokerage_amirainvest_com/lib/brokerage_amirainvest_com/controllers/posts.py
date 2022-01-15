from sqlalchemy import select

from common_amirainvest_com.schemas.schema import Posts, Users
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_user(session):
    user = Users(
            **{
                "sub": "",
                "name": "",
                "username": "",
                "picture_url": "",
                "email": "",
            }
        )
    session.add(user)
    return user.__dict__


@Session
async def get_user(session, user_id: str):
    return (await session.execute(select(Users).where(Users.id == user_id))).scalars().first()


@Session
async def create_trade_post(session, creator_id: str, plaid_user_id, transaction_id, action, security: str):
    user = await get_user(creator_id)
    post = Posts(
        **{
            "creator_id": user.id,
            "platform": "brokerage",  # BROKERAGE
            "platform_user_id": plaid_user_id,  # PLAID USER ID
            "platform_post_id": transaction_id,  # TRANSACTION_ID
            "profile_img_url": user.picture_url,
            "text": "",
            "title": generate_title(action, security),
            "chip_labels": user.chip_labels,
        }
    )
    session.add(post)
    return post


def generate_title(action, security):
    return f"{action} {security}"


if __name__ == '__main__':
    from pprint import pprint
    print(run_async_function_synchronously(create_trade_post, "c148fde2-5e22-49a1-a4ae-84b9cb6aec73"))
