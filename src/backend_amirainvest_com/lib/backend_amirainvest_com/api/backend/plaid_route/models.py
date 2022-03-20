from typing import Optional

from pydantic import BaseModel


class PlaidTokenRequest(BaseModel):
    public_token: str
    is_update: bool


class UpdatePlaidTokenRequest(BaseModel):
    item_id: str
    redirect_uri: str


class LinkTokenResponse(BaseModel):
    link_token: str


class CurrentPlaidAccounts(BaseModel):
    item_id: str
    plaid_institution_id: Optional[str]
    account_name: str
    account_mask: str


class FinancialAccount(BaseModel):
    item_id: str
    institution_name: str
    account_name: str
    status: str
    account_type: str
    account_sub_type: str
