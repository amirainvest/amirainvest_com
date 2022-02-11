import asyncio
import decimal
from datetime import date, datetime
from typing import Optional, Tuple

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import (
    FinancialAccountCurrentHoldings,
    FinancialAccountHoldingsHistory,
    FinancialAccounts,
    FinancialAccountTransactions,
    MarketHolidays,
    PlaidSecurities,
    Securities,
    SecurityPrices,
)
from common_amirainvest_com.utils.decorators import Session


class Account(BaseModel):
    id: int
    user_id: str
    cash: decimal.Decimal
    holdings: list[FinancialAccountHoldingsHistory]


# TODO should we have a holdings and a price date(e.g., a price_date could be price time could be priced further back
#  than a holding?
# TODO add a buy_back date so its easier to query on the frontend ....


async def run(user_id: str):
    accounts = await get_financial_accounts(user_id=user_id)
    market_holidays = await get_market_holidays_dict()

    # Run For History
    # end_date = datetime.now().replace(hour=21, minute=0, second=0, microsecond=0) - relativedelta(years=2)
    end_date = datetime.utcnow().replace(month=1, day=1, hour=21, minute=0, second=0, microsecond=0)
    today = datetime.now().replace(hour=21, minute=0, second=0, microsecond=0)
    for account in accounts:
        transactions_by_date = await get_financial_transactions_dict(account_id=account.id)
        holdings = await get_current_financial_holdings(account_id=account.id)

        historical_account = Account(id=account.id, user_id=user_id, holdings=[], cash=0)
        for holding in holdings:
            security_id = await get_security_id_by_plaid_security_id(holding.plaid_security_id)
            if holding.security_id == "":  # TODO define cash here..
                historical_account.cash = holding.price
            historical_account.holdings.append(
                FinancialAccountHoldingsHistory(
                    account_id=holding.account_id,
                    plaid_security_id=holding.plaid_security_id,
                    security_id=security_id,
                    user_id=user_id,
                    price=holding.price,
                    price_time=holding.price_time,
                )
            )

        historical_holdings: list = [historical_account]
        while today >= end_date:
            if today.date() in market_holidays or today.weekday() > 4:
                continue

            today_holdings = historical_holdings[len(historical_holdings) - 1]
            if today.date() in transactions_by_date:
                transactions = transactions_by_date[today.date()]
                for transaction in transactions:
                    today_holdings = perform_transaction(today_holdings, transaction)

            tomorrow_holdings = Account(
                id=today_holdings.id, user_id=today_holdings.user_id, holdings=[], cash=today_holdings.cash
            )
            tomorrow = today - relativedelta(days=1)

            for holding in today_holdings.holdings:
                # TODO can we ever have a negative quantity holding
                if 0 >= holding.quantity:
                    continue

                # TODO Support options contract pricing
                security_price = await get_closest_price(holding.security_id, tomorrow)
                tomorrow_holdings.holdings.append(
                    FinancialAccountHoldingsHistory(
                        account_id=holding.account_id,
                        plaid_security_id=holding.plaid_security_id,
                        security_id=holding.security_id,
                        user_id=holding.user_id,
                        price=security_price.price,
                        price_time=tomorrow,
                        quantity=holding.quantity,
                    )
                )

            historical_holdings.append(tomorrow_holdings)
            today = tomorrow

        insertable = []
        cash_security = await get_cash_security()
        for historical_holding in historical_holdings:
            cash_holding = FinancialAccountHoldingsHistory(
                account_id=historical_holding.account_id,
                plaid_security_id=historical_holding.plaid_security_id,
                security_id=cash_security.id,
                user_id=historical_holding.user_id,
                price=historical_holding.price,
                price_time=historical_holding.price_time,
                quantity=1 * historical_holding.price,
            )
            insertable.append(cash_holding)
            insertable.extend(historical_holding.holdings)
        await insert_historical_holdings(insertable)


async def buy_buy(account_holdings: Account, transaction: FinancialAccountTransactions) -> Account:
    account_holdings.cash = account_holdings.cash + transaction.value_amount
    current_holding, index = get_current_holding_if_exists(transaction=transaction, holdings=account_holdings.holdings)
    if current_holding is not None and index is not None:
        current_holding.quantity = current_holding.quantity - transaction.quantity
        # TODO if we modify variable, does that update the underlying type in the array?
        account_holdings.holdings[index] = current_holding
    return account_holdings


async def sell_sell(account_holdings: Account, transaction: FinancialAccountTransactions) -> Account:
    account_holdings.cash = account_holdings.cash - transaction.value_amount
    current_holding, index = get_current_holding_if_exists(transaction=transaction, holdings=account_holdings.holdings)
    if current_holding is None:
        sec_id = await get_security_id_by_plaid_security_id(transaction.security_id)
        account_holdings.holdings.append(
            FinancialAccountHoldingsHistory(
                account_id=account_holdings.id,
                plaid_security_id=transaction.security_id,
                security_id=sec_id,
                user_id=account_holdings.user_id,
                price=transaction.price,
                price_time=None,
                quantity=transaction.quantity,
            )
        )
    elif index is not None:
        current_holding.quantity = current_holding.quantity + transaction.quantity
        current_holding.price = transaction.price
        account_holdings.holdings[index] = current_holding
    else:
        raise Exception("...?")
    return account_holdings


rule_set = {"buy": {"buy": buy_buy}, "sell": {"sell": sell_sell}}


async def perform_transaction(account_holdings: Account, transaction: FinancialAccountTransactions) -> Account:
    try:
        account_holdings = await rule_set[transaction.type][transaction.subtype](account_holdings, transaction)
    except KeyError:
        raise Exception(".... we didnt check for this key ....")  # TODO error message...
    return account_holdings


def get_current_holding_if_exists(
    transaction: FinancialAccountTransactions, holdings: list[FinancialAccountHoldingsHistory]
) -> Tuple[Optional[FinancialAccountHoldingsHistory], Optional[int]]:
    for idx, holding in enumerate(holdings):
        if transaction.security_id == holding.plaid_security_id:
            return holding, idx
    return None, None


@Session
async def insert_historical_holdings(session: AsyncSession, historical_holdings: list[FinancialAccountHoldingsHistory]):
    session.add_all(historical_holdings)


@Session
async def get_cash_security(session: AsyncSession) -> Optional[Securities]:
    # TODO should we use a different security id, what if we buy on the FX?
    response = await session.execute(select(Securities).where(Securities.ticker_symbol == "CUR:USD"))
    return response.scalar()


@Session
async def get_closest_price(
    session: AsyncSession, security_id: int, posting_date: datetime
) -> Optional[SecurityPrices]:
    response = await session.execute(
        select(SecurityPrices)
        .join(Securities)
        .where(Securities.id == security_id, SecurityPrices.price_time <= posting_date)
        .order_by(SecurityPrices.price_time.desc())
        .limit(1)
    )
    return response.scalar()


@Session
async def get_security_id_by_plaid_security_id(session: AsyncSession, plaid_security_id: int) -> Optional[int]:
    plaid_response = await session.execute(select(PlaidSecurities).where(PlaidSecurities.id == plaid_security_id))
    plaid_security = plaid_response.one()
    security_response = await session.execute(
        select(Securities).where(Securities.ticker_symbol == plaid_security.ticker_symbol)
    )
    security = security_response.scalar()
    if security is None:
        return None
    return security.id


@Session
async def get_market_holidays_dict(session: AsyncSession) -> dict[MarketHolidays, None]:
    response = await session.execute(select(MarketHolidays))

    holiday_dict: dict[MarketHolidays, None] = {}
    for holiday in response.scalars().all():
        holiday_dict[holiday.date.date()] = None
    return holiday_dict


@Session
async def get_financial_transactions_dict(
    session: AsyncSession, account_id: str
) -> dict[date, list[FinancialAccountTransactions]]:
    response = await session.execute(
        select(FinancialAccountTransactions).where(FinancialAccountTransactions.account_id == account_id)
    )

    transaction_history_day_dict: dict[date, list[FinancialAccountTransactions]] = {}
    for item in response.scalars().all():
        try:
            transaction_history_day_dict[item.posting_date].append(item)
        except KeyError:
            transaction_history_day_dict[item.posting_date.date()] = [item]
    return transaction_history_day_dict


@Session
async def get_current_financial_holdings(
    session: AsyncSession, account_id: int
) -> list[FinancialAccountCurrentHoldings]:
    response = await session.execute(
        select(FinancialAccountCurrentHoldings).where(FinancialAccountCurrentHoldings.account_id == account_id)
    )
    return response.scalars().all()


@Session
async def get_financial_accounts(session: AsyncSession, user_id: str) -> list[FinancialAccounts]:
    response = await session.execute(select(FinancialAccounts).where(FinancialAccounts.user_id == user_id))
    return response.scalars().all()


if __name__ == "__main__":
    asyncio.run(run(user_id="f6b8bdfc-5a9d-11ec-bc23-0242ac1a0002"))
