from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.dynamo.utils import create_table
from common_amirainvest_com.schemas.schema import (
    FinancialAccounts,
    FinancialAccountTransactions,
    FinancialInstitutions,
    Securities,
)
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
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
async def get_securities_by_plaid_ids(session: AsyncSession, ids: list[str]) -> list[Securities]:
    existing_securities_res = await session.execute(select(Securities).where(Securities.plaid_security_id.in_(ids)))
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
async def get_investment_transactions_by_plaid_id(
    session: AsyncSession, ids: list[str]
) -> list[FinancialAccountTransactions]:
    result = await session.execute(
        select(FinancialAccountTransactions).where(
            FinancialAccountTransactions.plaid_investment_transaction_id.in_(ids)
        )
    )
    return result.scalars().all()


async def test():
    await create_table("brokerage_users", "user_id")


if __name__ == "__main__":
    run_async_function_synchronously(test)