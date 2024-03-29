import hashlib
import hmac
import json
import time

import jwt
import requests
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from jose import jwt as j_jwt  # type: ignore
from pydantic import BaseModel

from backend_amirainvest_com.controllers import plaid_controller as plaid
from common_amirainvest_com.utils.consts import AUTH0_API_AUDIENCE, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN


http_bearer_scheme = HTTPBearer()
jwks_client = jwt.PyJWKClient(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")


async def _auth_dep(
    security_scopes: SecurityScopes,
    bearer_auth_creds,
):
    """
    This is used so that tests can overwrite the auth logic. Depends() messes with pytest
    """
    token = bearer_auth_creds.credentials
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[
                "RS256",
            ],
            audience=AUTH0_API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")
    return payload


# TODO add validating security scopes
# TODO make all 403s return the same error
async def auth_dep(
    security_scopes: SecurityScopes,
    bearer_auth_creds: HTTPAuthorizationCredentials = Depends(http_bearer_scheme),
):
    return await _auth_dep(security_scopes, bearer_auth_creds)


async def auth_depends(data=Security(auth_dep, scopes=[])):
    return data


async def auth_depends_user_id(data=Security(auth_dep, scopes=[])):
    if "https://amirainvest.com/user_id" not in data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")
    data["https://amirainvest.com/user_id"] = str(data["https://amirainvest.com/user_id"])
    return data


def get_application_token():
    return requests.post(
        url=f"https://{AUTH0_DOMAIN}/oauth/token",
        data=json.dumps(
            {
                "client_id": AUTH0_CLIENT_ID,
                "client_secret": AUTH0_CLIENT_SECRET,
                "audience": AUTH0_API_AUDIENCE,
                "grant_type": "client_credentials",
            }
        ),
        headers={"content-type": "application/json"},
    ).json()["access_token"]


KEY_CACHE: dict[str, dict] = {}


def verify_webhook(body: BaseModel, signed_jwt: str) -> bool:
    current_key_id = j_jwt.get_unverified_header(signed_jwt)["kid"]
    # If the key is not in the cache, update all non-expired keys.
    if current_key_id not in KEY_CACHE:
        keys_ids_to_update = [key_id for key_id, key in KEY_CACHE.items() if key["expired_at"] is None]
        keys_ids_to_update.append(current_key_id)

        for key_id in keys_ids_to_update:
            KEY_CACHE[key_id] = plaid.webhook_verify(key_id)

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
        claims = j_jwt.decode(signed_jwt, key, algorithms=["ES256"])
    except j_jwt.JWTError:
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
