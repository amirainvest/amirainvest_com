from enum import Enum
from typing import Optional, Tuple

from fastapi import HTTPException, status
from pydantic import BaseModel, Field
from starlette.requests import Request


def get_authorization_scheme_param(authorization_header_value: str) -> Tuple[str, str]:
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param


class SecuritySchemeType(Enum):
    apiKey = "apiKey"
    http = "http"
    oauth2 = "oauth2"
    openIdConnect = "openIdConnect"


class SecurityBaseModel(BaseModel):
    type_: SecuritySchemeType = Field(..., alias="type")
    description: Optional[str] = None

    class Config:
        extra = "allow"


class APIKeyIn(Enum):
    query = "query"
    header = "header"
    cookie = "cookie"


class APIKey(SecurityBaseModel):
    type_ = Field(SecuritySchemeType.apiKey, alias="type")
    in_: APIKeyIn = Field(..., alias="in")
    name: str


class HTTPBase(SecurityBaseModel):
    type_ = Field(SecuritySchemeType.http, alias="type")
    scheme: str


class HTTPBearerModel(HTTPBase):
    scheme = "bearer"
    bearerFormat: Optional[str] = None


class SecurityBase:
    model: SecurityBaseModel
    scheme_name: str


class HTTPAuthorizationCredentials(BaseModel):
    scheme: str
    credentials: str


class HTTPBearer(SecurityBase):
    def __init__(
        self,
        *,
        bearerFormat: Optional[str] = None,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        self.model = HTTPBearerModel(bearerFormat=bearerFormat, description=description)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        authorization: str = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")
            else:
                return None
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication credentials",
                )
            else:
                return None
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)
