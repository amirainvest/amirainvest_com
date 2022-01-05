import plaid  # type: ignore
import requests
from plaid.api import plaid_api  # type: ignore
from plaid.model.country_code import CountryCode  # type: ignore
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest  # type: ignore
from plaid.model.item_public_token_exchange_response import ItemPublicTokenExchangeResponse  # type: ignore
from plaid.model.link_token_create_request import LinkTokenCreateRequest  # type: ignore
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser  # type: ignore
from plaid.model.products import Products  # type: ignore

from common_amirainvest_com.utils.consts import PLAID_APPLICATION_NAME, PLAID_CLIENT_ID, PLAID_ENVIRONMENT, PLAID_SECRET


configuration = plaid.Configuration(
    host=PLAID_ENVIRONMENT, api_key={"clientId": PLAID_CLIENT_ID, "secret": PLAID_SECRET}
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)


def generate_link_token(user_id: str) -> str:
    # TODO Do we have any other meta-data we want to pass plaid for a user?
    # TODO Do we want to support any other country codes outside of us?
    request = LinkTokenCreateRequest(
        products=[Products("investments"), Products("transactions")],
        client_name=PLAID_APPLICATION_NAME,
        country_codes=[CountryCode("US")],
        language="en",
        user=LinkTokenCreateRequestUser(client_user_id=user_id),
    )
    response = client.link_token_create(request)
    return response["link_token"]


def exchange_public_for_access_token(public_token: str) -> ItemPublicTokenExchangeResponse:
    exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
    return client.item_public_token_exchange(exchange_request)


def webhook_verify(key_id: str) -> dict:
    # Debug the SDK and get this to work using the SDK rather than requests
    r = requests.post(
        f"https://{PLAID_ENVIRONMENT}.plaid.com/webhook_verification_key/get",
        json={"client_id": PLAID_CLIENT_ID, "secret": PLAID_SECRET, "key_id": key_id},
    )

    # If this is the case, the key ID may be invalid.
    if r.status_code != 200:
        # TODO Raise Exception...?
        return {}

    response = r.json()
    return response["key"]
