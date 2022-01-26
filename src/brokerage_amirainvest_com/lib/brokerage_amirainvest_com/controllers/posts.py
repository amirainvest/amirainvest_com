from sqlalchemy import select

from common_amirainvest_com.schemas.schema import FinancialAccounts, FinancialAccountTransactions, Posts, Users
from common_amirainvest_com.utils.decorators import Session
from data_imports_amirainvest_com.controllers import posts


@Session
async def get_user(session, user_id: str):
    return (await session.execute(select(Users).where(Users.id == user_id))).scalars().first()


@Session
async def create_trade_post(session, creator_id: str, plaid_user_id, transaction_id, action, security: str):
    user = await get_user(creator_id)
    post = Posts(
        **{
            "creator_id": user.id,
            "platform": "brokerage",
            "platform_user_id": plaid_user_id,
            "platform_post_id": transaction_id,
            "profile_img_url": user.picture_url,
            "text": generate_title(action, security),
            "title": generate_title(action, security),
            "chip_labels": user.chip_labels,
        }
    )
    session.add(post)
    return post


@Session
async def get_day_transactions(session):
    return [
        x._asdict()
        for x in (
            (
                await session.execute(
                    select(FinancialAccounts, FinancialAccountTransactions).join(FinancialAccounts)
                    # .where(extract("day", FinancialAccountTransactions.created_at) == datetime.today().day)
                )
            ).all()
        )
    ]


async def create_day_transaction_posts():
    day_transactions = await get_day_transactions()
    for transaction_data in day_transactions:
        account = transaction_data["FinancialAccounts"].dict()
        transaction = transaction_data["FinancialAccountTransactions"].dict()
        post = await create_trade_post(
            account["user_id"],
            account["plaid_id"],
            transaction["plaid_investment_transaction_id"],
            transaction["type"],
            transaction["name"],
        )
        post_data = {k: str(v) for k, v in post.dict().items() if k in Posts.__dict__ and v}
        posts.put_post_on_creators_redis_feeds(post_data)
        await posts.put_post_on_subscriber_redis_feeds(post_data, "premium")


def generate_title(action, security):
    return f"{action} {security}"
