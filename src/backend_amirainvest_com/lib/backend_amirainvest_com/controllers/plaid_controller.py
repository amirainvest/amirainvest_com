import plaid  # type: ignore
import requests
from fastapi import HTTPException, status
from plaid.api import plaid_api  # type: ignore
from plaid.model.country_code import CountryCode  # type: ignore
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest  # type: ignore
from plaid.model.item_public_token_exchange_response import ItemPublicTokenExchangeResponse  # type: ignore
from plaid.model.link_token_create_request import LinkTokenCreateRequest  # type: ignore
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser  # type: ignore
from plaid.model.products import Products  # type: ignore

from common_amirainvest_com.dynamo.utils import get_brokerage_user_item
from common_amirainvest_com.utils.consts import (
    PLAID_APPLICATION_NAME,
    PLAID_CLIENT_ID,
    PLAID_ENVIRONMENT,
    PLAID_SECRET,
    PLAID_WEBHOOK,
)


configuration = plaid.Configuration(
    host=PLAID_ENVIRONMENT, api_key={"clientId": PLAID_CLIENT_ID, "secret": PLAID_SECRET}
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)


async def generate_link_token(user_id: str, item_id: str, redirect_uri: str) -> str:
    request = LinkTokenCreateRequest(
        client_name=PLAID_APPLICATION_NAME,
        language="en",
        country_codes=[CountryCode("US")],
        user=LinkTokenCreateRequestUser(client_user_id=user_id),
        products=[Products("investments"), Products("transactions")],
        webhook=PLAID_WEBHOOK,
    )

    if redirect_uri != "":
        request.redirect_uri = redirect_uri

    if item_id != "":
        brokerage_user = await get_brokerage_user_item(user_id=user_id, item_id=item_id)
        if brokerage_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="could not find item id")
        request.access_token = brokerage_user.access_token
        request.products = []

    response = client.link_token_create(request)
    return response["link_token"]


def exchange_public_for_access_token(public_token: str) -> ItemPublicTokenExchangeResponse:
    exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
    return client.item_public_token_exchange(exchange_request)


def webhook_verify(key_id: str) -> dict:
    # Debug the SDK and get this to work using the SDK rather than requests

    r = requests.post(
        f"{PLAID_ENVIRONMENT}/webhook_verification_key/get",
        json={"client_id": PLAID_CLIENT_ID, "secret": PLAID_SECRET, "key_id": key_id},
    )

    # If this is the case, the key ID may be invalid.
    if r.status_code != 200:
        # TODO Raise Exception...?
        return {}

    response = r.json()
    return response["key"]
