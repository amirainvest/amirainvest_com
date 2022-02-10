from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession
from common_amirainvest_com.schemas.schema import (
    FinancialAccounts,
    FinancialAccountTransactions,
    FinancialAccountCurrentHoldings,
    SubscriptionLevel,
    MediaPlatform,
    Posts,
    Users,
    Securities,
)
# from common_amirainvest_com.controllers.creator import Creator, get_creator_attributes
from common_amirainvest_com.utils.decorators import Session
from data_imports_amirainvest_com.controllers import posts
from datetime import datetime
from functools import lru_cache


@Session
async def get_user(session, user_id: str):
    return (await session.execute(select(Users).where(Users.id == user_id))).scalars().first()


@Session
async def create_trade_post(
    session: AsyncSession,
    creator_id: str,
    plaid_user_id,
    transaction_id,
    transaction_type: str,
    transaction_subtype: str,
    security: str
):
    post = Posts(
        **{
            "creator_id": creator_id,
            "subscription_level": SubscriptionLevel.standard,
            "title": None,
            "content": generate_content(transaction_type, transaction_subtype, security),
            "photos": [],

            "platform": MediaPlatform.brokerage,
            "platform_display_name": None,
            "platform_user_id": plaid_user_id,
            "platform_img_url": None,
            "platform_profile_url": None,
            "twitter_handle": None,

            "platform_post_id": transaction_id,
            "platform_post_url": None,
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
                    .where(extract("day", FinancialAccountTransactions.created_at) == datetime.today().day)
                )
            ).all()
        )
    ]


async def create_day_transaction_posts():
    trade_posts = []
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


@Session
async def get_current_holdings(session: AsyncSession, user_id: str):
    return [x.dict() for x in (
        await session.execute(
            select(
                FinancialAccountCurrentHoldings, Securities
            ).join(
                Securities
            ).where(
                FinancialAccountCurrentHoldings.user_id == user_id
            )
        )
        ).scalars().all()]


async def get_existing_holding(creator_id: str, security: str):
    holdings = await get_current_holdings(creator_id)
    for holding in holdings:
        if holding.security == security:
            return True, holding
    return False, None


async def get_portfolio_value(creator_id: str):
    portfolio_value = 0
    holdings = await get_current_holdings(creator_id)
    for holding in holdings:
        portfolio_value += (holding.quantity * holding.latest_price)
    return portfolio_value


async def get_trade_attributes(
    creator_id: str, transaction_type: str, transaction_subtype: str, security: str, transaction_value: float
):
    is_existing, holding = await get_existing_holding(creator_id, security)
    portfolio_value = await get_portfolio_value(creator_id)
    percentage_of_portfolio = transaction_value / portfolio_value
    if is_existing:
        if transaction_value > 0:
            start = "increased"
        else:
            start = "decreased"
            if abs(transaction_value) == (holding.quantity * holding.latest_price):
                start = "closed"
    else:
        start = "open"
    end = "long"
    return percentage_of_portfolio, f"{start}_{end}"


def generate_content(
    creator_id: str, transaction_type: str, transaction_subtype: str, security: str, transaction_value: float
):
    percentage_of_portfolio, trade_action = get_trade_attributes(
        creator_id, transaction_type, transaction_subtype, security, transaction_value
    )
    return {
        "open_long": f"Opened {percentage_of_portfolio}% position in {security}",
        "open_short": f"Opened {percentage_of_portfolio}% short position in {security}",
        "closed_long": f"Closed {percentage_of_portfolio}% position in {security}",
        "closed_short": f"Closed {percentage_of_portfolio}% short position in {security}",
        "increased_long": f"Increased position in {security} by {percentage_of_portfolio}%",
        "increased_short": f"Increased short position in {security} by {percentage_of_portfolio}%",
        "decreased_long": f"Decreased position in {security} by {percentage_of_portfolio}%",
        "decreased_short": f"Decreased short position in {security} by {percentage_of_portfolio}%",
    }[trade_action]


if __name__ == '__main__':
    from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
    run_async_function_synchronously(get_current_holdings, "")
