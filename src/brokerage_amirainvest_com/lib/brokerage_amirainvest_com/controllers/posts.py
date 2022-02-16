from datetime import datetime

from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from common_amirainvest_com.schemas.schema import (
    FinancialAccountCurrentHoldings,
    FinancialAccounts,
    FinancialAccountTransactions,
    MediaPlatform,
    PlaidSecurities,
    Posts,
    Securities,
    SubscriptionLevel,
    Users,
)
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_user(session: AsyncSession, user_id: str):
    return (await session.execute(select(Users).where(Users.id == user_id))).scalars().first()


@Session
async def create_trade_post(
    session: AsyncSession,
    creator_id: str,
    plaid_user_id,
    transaction_id,
    transaction_value: float,
    security_ticker: str,
) -> Posts:
    post = Posts(
        creator_id=creator_id,
        subscription_level=SubscriptionLevel.standard,
        title=None,
        content=(await generate_content(creator_id, security_ticker, transaction_value)),
        photos=[],
        platform=MediaPlatform.brokerage,
        platform_display_name=None,
        platform_user_id=plaid_user_id,
        platform_img_url=None,
        platform_profile_url=None,
        twitter_handle=None,
        platform_post_id=transaction_id,
        platform_post_url=None,
    )
    session.add(post)
    return post


# TODO We should probably have another table that joins plaid securities and securities in some capacity
#   other option is to put a security_id on the PlaidSecurities table, or the Transactions table...etc...
@Session
async def get_day_transactions(session: AsyncSession):
    return (
        await session.execute(
            select(FinancialAccounts, FinancialAccountTransactions, Securities)
            .join(FinancialAccounts)
            .join(PlaidSecurities.id == FinancialAccountTransactions.plaid_security_id)
            .join(Securities, Securities.ticker_symbol == PlaidSecurities.ticker_symbol)
            .where(extract("day", FinancialAccountTransactions.created_at) == datetime.today().day)
        )
    ).all()


async def create_day_transaction_posts():
    day_transactions = await get_day_transactions()
    for transaction_data in day_transactions:
        transaction_data = transaction_data._asdict()
        account = transaction_data["FinancialAccounts"].dict()
        transaction = transaction_data["FinancialAccountTransactions"].dict()
        security = transaction_data["Securities"].dict()
        await create_trade_post(
            account["user_id"],
            account["plaid_id"],
            transaction["plaid_investment_transaction_id"],
            transaction["value_amount"],
            security["ticker_symbol"],
        )


@Session
async def get_current_holdings(session: AsyncSession, user_id: str):
    return (
        await session.execute(
            select(FinancialAccountCurrentHoldings, Securities)
            .join(Securities, Securities.id == FinancialAccountCurrentHoldings.plaid_security_id)
            .where(FinancialAccountCurrentHoldings.user_id == user_id)
        )
    ).all()


async def get_existing_holding(creator_id: str, security_ticker: str):
    holdings = await get_current_holdings(creator_id)
    for holding in holdings:
        holding = holding._asdict()
        security = holding["Securities"].dict()
        if security["ticker_symbol"] == security_ticker:
            return True, holding
    return False, None


async def get_user_portfolio_value(creator_id: str):
    portfolio_value = 0
    holdings = await get_current_holdings(creator_id)
    for holding in holdings:
        holding = holding._asdict()
        current_holding = holding["FinancialAccountCurrentHoldings"].dict()
        portfolio_value += current_holding["quantity"] * current_holding["latest_price"]
    return portfolio_value


async def get_trade_attributes(creator_id: str, security_ticker: str, transaction_value: float):
    previously_owned, holding = await get_existing_holding(creator_id, security_ticker)
    portfolio_value = await get_user_portfolio_value(creator_id)
    percentage_of_portfolio = round((transaction_value * 100 / portfolio_value), 4)
    if previously_owned:
        if transaction_value > 0:
            start = "increased"
        else:
            start = "decreased"
            if abs(transaction_value) == (
                holding["FinancialAccountCurrentHoldings"].quantity
                * holding["FinancialAccountCurrentHoldings"].latest_price
            ):
                start = "closed"
    else:
        start = "open"
    end = "long"
    return percentage_of_portfolio, f"{start}_{end}"


async def generate_content(creator_id: str, security_ticker: str, transaction_value: float):
    percentage_of_portfolio, trade_action = await get_trade_attributes(creator_id, security_ticker, transaction_value)
    text = {
        "open_long": f"Opened {percentage_of_portfolio}% position in {security_ticker}",
        "open_short": f"Opened {percentage_of_portfolio}% short position in {security_ticker}",
        "closed_long": f"Closed {percentage_of_portfolio}% position in {security_ticker}",
        "closed_short": f"Closed {percentage_of_portfolio}% short position in {security_ticker}",
        "increased_long": f"Increased position in {security_ticker} by {percentage_of_portfolio}%",
        "increased_short": f"Increased short position in {security_ticker} by {percentage_of_portfolio}%",
        "decreased_long": f"Decreased position in {security_ticker} by {percentage_of_portfolio}%",
        "decreased_short": f"Decreased short position in {security_ticker} by {percentage_of_portfolio}%",
    }[trade_action]
    return f"""<p>{text}</p>"""
