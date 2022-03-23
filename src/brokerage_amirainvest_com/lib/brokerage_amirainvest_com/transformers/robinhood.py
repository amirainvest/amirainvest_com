from datetime import datetime

from brokerage_amirainvest_com.repository import get_cash_security_plaid
from brokerage_amirainvest_com.transformers.transformer import BrokerageTransformer
from common_amirainvest_com.schemas.schema import (
    FinancialAccountCurrentHoldings,
    FinancialAccounts,
    FinancialAccountTransactions,
)


class Robinhood(BrokerageTransformer):
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
        # Iterate over financial accounts and just return the non-cash account
        new_accounts = []
        for fa in financial_accounts:
            if fa.type == "depository" and fa.sub_type == "checking":
                continue
            new_accounts.append(fa)

        return new_accounts

    async def transform_holdings(
        self,
        financial_accounts: list[FinancialAccounts],
        financial_transactions: list[FinancialAccountTransactions],
        financial_holdings: list[FinancialAccountCurrentHoldings],
    ) -> list[FinancialAccountCurrentHoldings]:
        # iterate over accounts and allocate the cash ones as a holding
        # Iterate over financial accounts and just return the non-cash account
        cash_account = None
        brokerage_account = None
        for fa in financial_accounts:
            if fa.type == "depository" and fa.sub_type == "checking":
                cash_account = fa
                continue
            if fa.type == "investment" and fa.sub_type == "brokerage":
                brokerage_account = fa
                continue

        plaid_cash_security = await get_cash_security_plaid()
        new_holdings: list[FinancialAccountCurrentHoldings] = []
        cash_holding = FinancialAccountCurrentHoldings(
            account_id=brokerage_account.id,
            plaid_security_id=plaid_cash_security.id,
            institution_value=cash_account.current_funds,
            latest_price=1,
            quantity=cash_account.current_funds,
            cost_basis=None,
            iso_currency_code="USD",
            latest_price_date=datetime.now(),
        )

        new_holdings.append(cash_holding)
        for h in financial_holdings:
            new_holdings.append(h)

        return new_holdings
