from brokerage_amirainvest_com.transformers.transformer import BrokerageTransformer
from common_amirainvest_com.schemas.schema import (
    FinancialAccountCurrentHoldings,
    FinancialAccounts,
    FinancialAccountTransactions,
)


class ETrade(BrokerageTransformer):
    async def transform_transactions(
        self,
        financial_accounts: list[FinancialAccounts],
        financial_transactions: list[FinancialAccountTransactions],
        financial_holdings: list[FinancialAccountCurrentHoldings],
    ) -> list[FinancialAccountTransactions]:
        return financial_transactions

    async def transform_accounts(
        self,
        financial_accounts: list[FinancialAccounts],
        financial_transactions: list[FinancialAccountTransactions],
        financial_holdings: list[FinancialAccountCurrentHoldings],
    ) -> list[FinancialAccounts]:
        return financial_accounts

    async def transform_holdings(
        self,
        financial_accounts: list[FinancialAccounts],
        financial_transactions: list[FinancialAccountTransactions],
        financial_holdings: list[FinancialAccountCurrentHoldings],
    ) -> list[FinancialAccountCurrentHoldings]:
        return financial_holdings
