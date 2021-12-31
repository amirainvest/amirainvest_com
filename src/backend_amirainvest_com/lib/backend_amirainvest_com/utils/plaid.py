from typing import Optional

import plaid  # type: ignore
from plaid.api import plaid_api  # type: ignore
from plaid.model.webhook_verification_key_get_request import WebhookVerificationKeyGetRequest  # type: ignore
from pydantic import BaseModel

from common_amirainvest_com.utils.consts import PLAID_CLIENT_ID, PLAID_SECRET


plaid_cfg = plaid.Configuration(
    host=plaid.Environment.Sandbox, api_key={"clientId": PLAID_CLIENT_ID, "secret": PLAID_SECRET}
)

plaid_client = plaid_api.PlaidApi(plaid.ApiClient(plaid_cfg))


class VerifyToken(BaseModel):
    alg: str
    crv: str
    kid: str
    kty: str
    use: str
    x: str
    y: str
    created_at: int
    expired_at: Optional[int]


def verify_webhook_key(key_id) -> dict:
    request = WebhookVerificationKeyGetRequest(key_id=key_id)

    response = plaid_client.webhook_verification_key_get(request)
    return response["key"]
