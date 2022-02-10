from pydantic import BaseModel


class PlaidTokenRequest(BaseModel):
    public_token: str
