import hashlib
import hmac
import time

import requests
from fastapi import APIRouter, Header
from jose import jwt  # type: ignore
from pydantic import BaseModel

from backend_amirainvest_com.consts import PLAID_WEBHOOK_VERIFY_ENDPOINT
from backend_amirainvest_com.controllers import webhooks
from backend_amirainvest_com.models.webhooks import HoldingsUpdate, InvestmentsUpdate, TransactionsUpdate
from common_amirainvest_com.utils.consts import PLAID_CLIENT_ID, PLAID_SECRET


router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


# Used for Sandbox Testing -- Plaid only exposes transactions
@router.post("/plaid/transactions")
async def transactions_update(transactions: TransactionsUpdate, plaid_verification: str = Header(None)):
    if verify_webhook(transactions, plaid_verification) is not True:
        return


@router.post("/plaid/holdings")
async def holdings_update(holdings: HoldingsUpdate, plaid_verification: str = Header(None)):
    if verify_webhook(holdings, plaid_verification) is not True:
        return
    await webhooks.handle_holdings_change(holdings)


@router.post("/plaid/investments")
async def investments_update(investments: InvestmentsUpdate, plaid_verification: str = Header(None)):
    if verify_webhook(investments, plaid_verification) is not True:
        return
    await webhooks.handle_investments_change(investments)


KEY_CACHE: dict[str, dict] = {}


def verify_webhook(body: BaseModel, signed_jwt: str) -> bool:
    current_key_id = jwt.get_unverified_header(signed_jwt)["kid"]
    # If the key is not in the cache, update all non-expired keys.
    if current_key_id not in KEY_CACHE:
        keys_ids_to_update = [key_id for key_id, key in KEY_CACHE.items() if key["expired_at"] is None]
        keys_ids_to_update.append(current_key_id)

        for key_id in keys_ids_to_update:
            r = requests.post(
                PLAID_WEBHOOK_VERIFY_ENDPOINT,
                json={"client_id": PLAID_CLIENT_ID, "secret": PLAID_SECRET, "key_id": key_id},
            )

            # If this is the case, the key ID may be invalid.
            if r.status_code != 200:
                continue

            response = r.json()
            key = response["key"]
            KEY_CACHE[key_id] = key

    # If the key ID is not in the cache, the key ID may be invalid.
    if current_key_id not in KEY_CACHE:
        return False

    # Fetch the current key from the cache.
    key = KEY_CACHE[current_key_id]

    # Reject expired keys.
    if key["expired_at"] is not None:
        return False

    # Validate the signature and extract the claims.
    try:
        claims = jwt.decode(signed_jwt, key, algorithms=["ES256"])
    except jwt.JWTError:
        return False

    # Ensure that the token is not expired.
    if claims["iat"] < time.time() - 5 * 60:
        return False

    # Compute the has of the body.
    m = hashlib.sha256()
    m.update(body.json(indent=2).encode())
    body_hash = m.hexdigest()

    # Ensure that the hash of the body matches the claim.
    # Use constant time comparison to prevent timing attacks.
    return hmac.compare_digest(body_hash, claims["request_body_sha256"])
