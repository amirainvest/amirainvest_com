import json
from functools import wraps

import jwt
import requests
from fastapi import HTTPException
from fastapi.security import HTTPBearer

from common_amirainvest_com.utils.consts import AUTH0_API_AUDIENCE, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN


token_auth_scheme = HTTPBearer()


def auth_required(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        token = kwargs["token"]
        verification_data = VerifyToken(token.credentials).verify()
        if "status" in verification_data:
            raise HTTPException(status_code=403, detail=verification_data["message"])
        data = await function(*args, **kwargs)
        return data

    return wrapper


def get_application_token():
    return requests.post(
        url="https://dev-0nn4c3x4.us.auth0.com/oauth/token",
        data=json.dumps(
            {
                "client_id": AUTH0_CLIENT_ID,
                "client_secret": AUTH0_CLIENT_SECRET,
                "audience": AUTH0_API_AUDIENCE,
                "grant_type": "client_credentials",
            }
        ),
        headers={"content-type": "application/json"},
    ).json()


class VerifyToken:
    def __init__(self, token):
        self.token = token
        self.jwks_client = jwt.PyJWKClient(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")

    def verify(self):
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(self.token).key
        except (jwt.exceptions.PyJWKClientError, jwt.exceptions.DecodeError) as e:
            return {"status": "error", "message": str(e)}
        try:
            payload = jwt.decode(
                self.token,
                signing_key,
                algorithms="RS256",
                audience=AUTH0_API_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/",
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return payload


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_application_token())
