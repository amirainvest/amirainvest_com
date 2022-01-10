from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class PlaidError(BaseModel):
    error_type: str
    error_code: str
    error_message: str
    display_message: Optional[str]
    request_id: str
    causes: List[str]
    status: Optional[int]
    documentation_url: str
    suggested_action: str


# Item type is specifically for Plaid if we want to derive some other meta-data
class PlaidItem(BaseModel):
    item_id: str
    institution_id: Optional[str]
    webhook: Optional[str]
    error: Optional[PlaidError]
    available_products: List[str]
    billed_products: List[str]
    products: List[str]
    consent_expiration_time: Optional[str]
    update_type: str
    request_id: str


class SecurityType(Enum):
    cash = "cash"
    derivative = "derivative"
    equity = "equity"
    etf = "etf"
    fixed_income = "fixed income"
    loan = "loan"
    mutual_fund = "mutual fund"
    other = "other"


class Security(BaseModel):
    security_id: str
    isin: Optional[str]
    cusip: Optional[str]
    sedol: Optional[str]
    institution_security_id: Optional[str]
    institution_id: Optional[str]
    proxy_security_id: Optional[str]
    name: Optional[str]
    ticker_symbol: Optional[str]
    is_cash_equivalent: Optional[bool]
    type: Optional[SecurityType]
    close_price: Optional[Decimal]
    close_price_as_of: Optional[date]  # Better datetime here...
    iso_currency_code: Optional[str]
    unofficial_currency_code: Optional[str]


class AccountType(Enum):
    credit = "credit"
    depository = "depository"
    loan = "loan"
    brokerage = "brokerage"
    investment = "investment"
    other = "other"


class Account(BaseModel):
    item_id: str
    account_id: str
    mask: Optional[str]
    name: str
    official_name: Optional[str]
    type: AccountType
    subtype: Optional[str]  # We could make this an enum, but there are many... many... values
    available: Optional[Decimal]
    current: Optional[Decimal]
    iso_currency_code: Optional[str]
    unofficial_currency_code: Optional[str]
    limit: Optional[Decimal]


class InvestmentTransactionType(Enum):
    buy = "buy"
    sell = "sell"
    cancel = "cancel"
    cash = "cash"
    fee = "fee"
    transfer = "transfer"


class InvestmentTransaction(BaseModel):
    investment_transaction_id: str
    account_id: str
    security_id: Optional[str]
    # ISO 8601 date
    date: str
    name: str
    quantity: Decimal
    amount: Decimal
    price: Decimal
    fees: Optional[Decimal]
    type: InvestmentTransactionType
    subtype: str  # Could make this an enum, but excessive values -> how would we keep this up to date?
    iso_currency_code: Optional[str]
    unofficial_currency_code: Optional[str]


class Holding(BaseModel):
    account_id: str
    security_id: str
    institution_price: Decimal
    institution_price_as_of: Optional[str]
    institution_value: Decimal
    cost_basis: Optional[Decimal]
    quantity: Decimal
    iso_currency_code: Optional[str]
    unofficial_currency_code: Optional[str]


class InvestmentInformation(BaseModel):
    securities: dict[str, Security]
    investment_transactions: list[InvestmentTransaction]
    accounts: list[Account]
    total_investment_transactions: int


class HoldingInformation(BaseModel):
    securities: dict[str, Security]
    accounts: list[Account]
    holdings: list[Holding]


class Institution(BaseModel):
    total: int
    plaid_institution_id: str
    name: str
    oauth: bool  # Does institution has Oauth login flow
