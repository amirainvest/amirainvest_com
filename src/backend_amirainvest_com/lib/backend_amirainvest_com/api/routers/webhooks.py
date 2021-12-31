import hashlib
import hmac
import time

from fastapi import APIRouter, Header
from jose import jwt  # type: ignore

from backend_amirainvest_com.controllers import webhooks
from backend_amirainvest_com.models.webhooks import HoldingsUpdate, InvestmentsUpdate
from backend_amirainvest_com.utils.plaid import verify_webhook_key


router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/plaid/holdings")
async def holdings_update(holdings: HoldingsUpdate, plaid_verification: str = Header(None)):
    if verify_webhook(holdings.json(), plaid_verification) is not True:
        return
    await webhooks.handle_holdings_change(holdings)


@router.post("/plaid/investments")
async def investments_update(investments: InvestmentsUpdate, plaid_verification: str = Header(None)):
    if verify_webhook(investments.json(), plaid_verification) is not True:
        return
    await webhooks.handle_investments_change(investments)


def verify_webhook(body: str, verification_key: str) -> bool:
    verification_dict = jwt.get_unverified_header(verification_key)
    if verification_dict["alg"] != "ES256":
        return False

    key_id = verification_dict["kid"]
    key = verify_webhook_key(key_id=key_id)

    try:
        claims = jwt.decode(verification_key, key, algorithms=["ES256"])
    except jwt.JWTError:
        return False

    if claims["iat"] < time.time() - 5 * 60:
        return False

    m = hashlib.sha256()
    m.update(body.encode())
    body_hash = m.hexdigest()
    return hmac.compare_digest(body_hash, claims["request_body_sha256"])
