from functools import wraps

import jwt
from common_amirainvest_com.config import AUTH0_API_AUDIENCE, AUTH0_DOMAIN, AUTH0_ISSUER
from fastapi import status
from fastapi.security import HTTPBearer


token_auth_scheme = HTTPBearer()


def auth_required(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        token = kwargs["token"]
        response = kwargs["response"]
        verification_data = VerifyToken(token.credentials).verify()
        if "status" in verification_data:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return verification_data
        data = await function(*args, **kwargs)
        return data

    return wrapper


class VerifyToken:
    def __init__(self, token):
        self.token = token
        self.config = {
            "DOMAIN": AUTH0_DOMAIN,
            "API_AUDIENCE": AUTH0_API_AUDIENCE,
            "ALGORITHMS": "RS256",
            "ISSUER": AUTH0_ISSUER,
        }
        self.jwks_client = jwt.PyJWKClient(f'https://{self.config["DOMAIN"]}/.well-known/jwks.json')

    def verify(self):
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(self.token).key
        except (jwt.exceptions.PyJWKClientError, jwt.exceptions.DecodeError) as e:
            return {"status": "error", "msg": str(e)}
        try:
            payload = jwt.decode(
                self.token,
                signing_key,
                algorithms=self.config["ALGORITHMS"],
                audience=self.config["API_AUDIENCE"],
                issuer=self.config["ISSUER"],
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return payload
