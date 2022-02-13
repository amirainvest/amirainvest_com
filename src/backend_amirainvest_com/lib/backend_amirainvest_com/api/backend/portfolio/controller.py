from datetime import datetime, date
from decimal import Decimal
from typing import Optional
import asyncio
from pydantic import BaseModel

from sqlalchemy import asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func, label

from common_amirainvest_com.schemas.schema import (
    FinancialAccountCurrentHoldings,
    FinancialAccounts,
    FinancialAccountTransactions,
    PlaidSecurities,
    Securities,
    SecurityPrices,
    UserSubscriptions,
    FinancialAccountHoldingsHistory,
)
from common_amirainvest_com.utils.decorators import Session


"""
    sell,distribution = outflow of assets from a tax-advantaged account
    cash, account fee = fee's paid for account maintenance
    cash, contribution = inflow of assets into a tax-advantaged account
    cash, deposit = inflow of cash into an account
    cash, dividend = inflow of cash from a dividend
    cash, stock distribution = inflow of stock from a distribution
    cash, interest = inflow of cash from interest
    cash, legal fee = fees paid for legal charges or services
    cash, long-term capital gain = long-term capital gain received as cash
    cash, management fee = fees paid for investment management of a mutual fund or other pooled investment vehicle
    cash, margin expense = fees paid for maintaining debt
    cash, non-qualified dividend = inflow of cash from non-qualified dividend
    cash, non-resident tax = taxes paid on behalf of the investor for non-residency in investment jurisdiction
    cash, pending credit = pending inflow of cash
    cash, pending debit = pending outflow of cash
    cash, qualified dividend = inflow of cash fro ma qualified dividend
    cash, short-term capital gain = short-term capital gain received as cash
    cash, tax = taxes paid on behalf of the investor
    cash, tax withheld = taxes withheld on behalf of the customer
    cash, transfer fee = fees incurred for transfer of a holding or account
    cash, trust fee = fees related to administration of a trust account
    cash, unqualified gain = unqualified capital gain received as cash
    cash, withdrawl = outflow of cash from an account


"""


class MarketValue(BaseModel):
    price_time: datetime
    market_value: Decimal


@Session
async def get_monetary_transactions(
    session: AsyncSession, account_id: int
) -> dict[date, list[FinancialAccountTransactions]]:
    transactions_response = await session.execute(
        select(FinancialAccountTransactions)
            .where(FinancialAccountTransactions.account_id == account_id)
    )
    transactions = transactions_response.scalars().all()

    d: dict[date, list[FinancialAccountTransactions]] = {}
    for tx in transactions:
        try:
            d[tx.posting_date.date()].append(tx)
        except KeyError:
            d[tx.posting_date.date()] = [tx]
    return d


@Session
async def get_market_value_list(session: AsyncSession, account_id: int) -> list[MarketValue]:
    market_value_by_day_response = await session.execute(
        select(
            FinancialAccountHoldingsHistory.price_time,
            label(
                "market_value", func.sum(
                    func.abs(FinancialAccountHoldingsHistory.price * FinancialAccountHoldingsHistory.quantity)
                )
            )
        )
            .where(FinancialAccountHoldingsHistory.account_id == account_id)
            .group_by(FinancialAccountHoldingsHistory.price_time)
            .order_by(FinancialAccountHoldingsHistory.price_time.asc())
    )
    results = market_value_by_day_response.all()
    market_values = []
    for res in results:
        d = res._asdict()
        market_values.append(MarketValue(**d))
    return market_values


@Session
async def calculate_return(session: AsyncSession, user_id: str):
    response = await session.execute(select(FinancialAccounts).where(FinancialAccounts.user_id == user_id))
    accounts = response.scalars().all()
    for account in accounts:
        market_value_by_day = await get_market_value_list(account_id=account.id)
        transactions_by_date = await get_monetary_transactions(account_id=account)

        # Working bottom up
        time_weighted_return = 1
        for index, _ in enumerate(market_value_by_day[1:]):
            mv_today = market_value_by_day[index]
            mv_yesterday = market_value_by_day[index - 1]
            mv_today_value = mv_today.market_value
            mv_yesterday_value = mv_yesterday.market_value
            hpr = ((mv_today_value - mv_yesterday_value) / mv_today_value)
            time_weighted_return = time_weighted_return * (1 + hpr)
        time_weighted_return = time_weighted_return - 1
        # Need to factor in adding back dividends and subtracting withdrawls
        # We dont need to worry about dividends as that will be factored into
        #   cash when computing historical
        #   TODO check to make sure we should just factor in dividend transactions
        #       when doing historical data...
        #   This way, we only need to "remove" it...
        #
        # # HPR = ((MV1 - MV0 + D1 - CF1)/MV0)


@Session
async def get_user_subscription(session: AsyncSession, user_id: str, creator_id: str) -> Optional[UserSubscriptions]:
    response = await session.execute(
        select(UserSubscriptions)
            .where(UserSubscriptions.subscriber_id == user_id)
            .where(UserSubscriptions.creator_id == creator_id)
    )
    return response.scalar()


@Session
async def get_holdings(session: AsyncSession, user_id: str) -> list:
    response = await session.execute(
        select(FinancialAccountCurrentHoldings, PlaidSecurities)
            .join(PlaidSecurities)
            .where(
            FinancialAccountCurrentHoldings.user_id == user_id,
            PlaidSecurities.id == FinancialAccountCurrentHoldings.plaid_security_id,
        )
    )

    return response.all()


@Session
async def get_recent_stock_price(session: AsyncSession, ticker_symbol: str) -> Optional[SecurityPrices]:
    # We want to do a join and get the price of a security by symbol most recent time
    return (
        await session.execute(
            select(SecurityPrices)
                .join(Securities.id)
                .where(Securities.ticker_symbol == ticker_symbol)
                .order_by(SecurityPrices.price_time.desc())
                .limit(1)
        )
    ).scalar()


@Session
async def get_buy_date(
    session: AsyncSession, user_id: str, security_id: int, position_quantity: int
) -> Optional[datetime]:
    transactions_response = await session.execute(
        select(FinancialAccountTransactions)
            .join(FinancialAccounts)
            .where(FinancialAccounts.user_id == user_id, FinancialAccountTransactions.security_id == security_id)
            .order_by(asc(FinancialAccountTransactions.posting_date))
    )
    transactions = transactions_response.scalars().all()

    buy_date, qty = compute_buy_date(Decimal(0), transactions)
    if qty == position_quantity:
        return buy_date
    return compute_buy_date(Decimal(abs(position_quantity - qty)), transactions)[0]


def compute_buy_date(share_qty: Decimal, transactions: list[FinancialAccountTransactions]) -> tuple:
    buy_date = None
    for tx in transactions:
        if tx.type == "buy":
            share_qty = Decimal(share_qty) + tx.quantity
        if tx.type == "sell":
            share_qty = Decimal(share_qty) - tx.quantity

        if buy_date is None and tx.type == "buy":
            buy_date = tx.posting_date

        if buy_date is not None and tx.type == "buy" and share_qty == 0:
            buy_date = tx.posting_date

    return buy_date, share_qty


@Session
async def get_ticker_symbol_by_plaid_id(session: AsyncSession, plaid_id: int) -> Optional[PlaidSecurities]:
    return (await session.execute(select(PlaidSecurities).where(PlaidSecurities.id == plaid_id))).scalar()


@Session
async def get_trading_history(session: AsyncSession, user_id: str) -> list:
    response = await session.execute(
        select(FinancialAccountTransactions, PlaidSecurities)
            .join(FinancialAccounts)
            .join(PlaidSecurities)
            .where(FinancialAccounts.user_id == user_id)
            .order_by(FinancialAccountTransactions.posting_date.desc())
    )
    return response.all()


if __name__ == '__main__':
    asyncio.run(calculate_return(user_id="f6b8bdfc-5a9d-11ec-bc23-0242ac1a0002"))
