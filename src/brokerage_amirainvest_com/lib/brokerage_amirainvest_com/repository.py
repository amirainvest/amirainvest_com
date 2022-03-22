from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import (
    FinancialAccounts,
    FinancialAccountTransactions,
    FinancialInstitutions,
    PlaidItems,
    PlaidSecurities,
)
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_financial_account(session: AsyncSession, item_id: str) -> Optional[FinancialAccounts]:
    financial_account = await session.execute(select(FinancialAccounts).where(FinancialAccounts.plaid_id == item_id))
    return financial_account.scalar()


@Session
async def add_financial_account(session: AsyncSession, financial_account: FinancialAccounts):
    session.add(financial_account)
    return financial_account


@Session
async def get_securities_by_plaid_ids(session: AsyncSession, ids: list[str]) -> list[PlaidSecurities]:
    existing_securities_res = await session.execute(
        select(PlaidSecurities).where(PlaidSecurities.plaid_security_id.in_(ids))
    )
    return existing_securities_res.scalars().all()


@Session
async def get_institutions_by_plaid_ids(session: AsyncSession, ids: list[str]) -> list[FinancialInstitutions]:
    result = await session.execute(select(FinancialInstitutions).where(FinancialInstitutions.plaid_id.in_(ids)))
    return result.scalars().all()


@Session
async def get_accounts_by_plaid_ids(session: AsyncSession, ids: list[str]) -> list[FinancialAccounts]:
    result = await session.execute(select(FinancialAccounts).where(FinancialAccounts.plaid_id.in_(ids)))
    return result.scalars().all()


@Session
async def get_item_ids_by_user_id(session: AsyncSession, user_id: str) -> list[PlaidItems]:
    result = await session.execute(select(PlaidItems).where(PlaidItems.user_id == user_id))
    return result.scalars().all()


@Session
async def get_investment_transactions_by_plaid_id(
    session: AsyncSession, ids: list[str]
) -> list[FinancialAccountTransactions]:
    result = await session.execute(
        select(FinancialAccountTransactions).where(
            FinancialAccountTransactions.plaid_investment_transaction_id.in_(ids)
        )
    )
    return result.scalars().all()
