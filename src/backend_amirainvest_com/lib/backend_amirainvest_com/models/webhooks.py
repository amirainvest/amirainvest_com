from typing import Optional

from pydantic import BaseModel


class ErrorType(BaseModel):
    error_type: str
    error_code: str
    error_message: str
    display_message: str
    request_id: str
    status: int
    documentation_url: str
    suggested_action: str


class HoldingsUpdate(BaseModel):
    webhook_type: str
    webhook_code: str
    item_id: str
    error: Optional[ErrorType]
    new_holdings: int
    updated_holdings: int


class InvestmentsUpdate(BaseModel):
    webhook_type: str
    webhook_code: str
    item_id: str
    error: Optional[ErrorType]
    new_investments_transactions: int
    canceled_investments_transactions: int


class TransactionsUpdate(BaseModel):
    error: Optional[dict]
    item_id: str
    new_transactions: int
    webhook_code: str
    webhook_type: str
