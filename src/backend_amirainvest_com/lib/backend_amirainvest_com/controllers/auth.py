import json

import jwt
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes

from common_amirainvest_com.utils.consts import AUTH0_API_AUDIENCE, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN


http_bearer_scheme = HTTPBearer()
jwks_client = jwt.PyJWKClient(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")


# TODO add validating security scopes
async def auth_dep(security_scopes: SecurityScopes, bearer: HTTPAuthorizationCredentials = Depends(http_bearer_scheme)):
    token = bearer.credentials
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            token,
            signing_key,
            algorithms="RS256",
            audience=AUTH0_API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")
    return payload


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


if __name__ == "__main__":
    print(get_application_token())
