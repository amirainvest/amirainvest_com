import json

import httpx
from fastapi import HTTPException, status

from backend_amirainvest_com.api.backend.user_route.model import Http400Enum
from common_amirainvest_com.utils.consts import (
    AUTH0_MANAGEMENT_API_AUDIENCE,
    AUTH0_MANAGEMENT_CLIENT_ID,
    AUTH0_MANAGEMENT_CLIENT_SECRET,
    AUTH0_MANAGEMENT_DOMAIN,
)


async def _get_auth0_management_api_token() -> str:
    async with httpx.AsyncClient() as client:
        result = await client.post(
            url=f"https://{AUTH0_MANAGEMENT_DOMAIN}/oauth/token",
            data=json.dumps(
                {
                    "client_id": AUTH0_MANAGEMENT_CLIENT_ID,
                    "client_secret": AUTH0_MANAGEMENT_CLIENT_SECRET,
                    "audience": AUTH0_MANAGEMENT_API_AUDIENCE,
                    "grant_type": "client_credentials",
                }
            ),  # type: ignore
            headers={"content-type": "application/json"},
        )

    if result.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Http400Enum.auth0_app_metadata_failed.value.dict(),
        )
    token = result.json()["access_token"]
    return token


async def update_user_app_metadata(sub: str, app_metadata: dict):
    bearer_token = await _get_auth0_management_api_token()

    async with httpx.AsyncClient() as client:
        result = await client.patch(
            url=f"https://{AUTH0_MANAGEMENT_DOMAIN}/api/v2/users/{sub}",
            data=json.dumps({"app_metadata": app_metadata}),  # type: ignore
            headers={"content-type": "application/json", "Authorization": f"Bearer {bearer_token}"},
        )

    if result.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Http400Enum.auth0_app_metadata_failed.value.dict(),
        )
