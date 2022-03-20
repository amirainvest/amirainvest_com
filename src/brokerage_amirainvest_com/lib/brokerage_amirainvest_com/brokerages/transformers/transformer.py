import abc

from common_amirainvest_com.schemas.schema import (
    FinancialAccountCurrentHoldings,
    FinancialAccounts,
    FinancialAccountTransactions,
)


class BrokerageTransformer(abc.ABC):
    @abc.abstractmethod
    async def transform_transactions(
        self,
        financial_accounts: list[FinancialAccounts],
        financial_transactions: list[FinancialAccountTransactions],
        financial_holdings: list[FinancialAccountCurrentHoldings],
    ) -> list[FinancialAccountTransactions]:
        """
        Transform transactions returns a list of transactions transformed into our own internal schema
        """

    ...

    @abc.abstractmethod
    async def transform_accounts(
        self,
        financial_accounts: list[FinancialAccounts],
        financial_transactions: list[FinancialAccountTransactions],
        financial_holdings: list[FinancialAccountCurrentHoldings],
    ) -> list[FinancialAccounts]:
        """
        Transform accounts returns a list of accounts transformed into our own internal schema
        """
        ...

    @abc.abstractmethod
    async def transform_holdings(
        self,
        financial_accounts: list[FinancialAccounts],
        financial_transactions: list[FinancialAccountTransactions],
        financial_holdings: list[FinancialAccountCurrentHoldings],
    ) -> list[FinancialAccountCurrentHoldings]:
        """
        Transform holdings returns a list of holdings transformed into our own internal schema
        """
        ...
