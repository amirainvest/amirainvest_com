from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.dynamo.utils import create_table
from common_amirainvest_com.schemas.schema import FinancialAccounts
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


async def test():
    await create_table("brokerage_users", "user_id")


if __name__ == "__main__":
    run_async_function_synchronously(test)
