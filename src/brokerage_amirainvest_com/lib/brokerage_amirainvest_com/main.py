import uuid

from brokerage_amirainvest_com.brokerages import plaid_provider
from brokerage_amirainvest_com.consts import PLAID_CLIENT_ID, PLAID_SECRET
from brokerage_amirainvest_com.mocks import MockWithAccessToken
from brokerage_amirainvest_com.providers import Providers
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously


action = "HOLDINGS_COLLECTION"
if __name__ == "__main__":
    # User authentication token fetcher for each service -> replaced by Dynamo implementation
    # this way the provider doesn't need to know how to fetch a user token appropriately,
    # it just needs to fetch user token to make request against a service
    # TODO: Maybe we wire this up in the providers class itself for registered providers?
    token_repository = MockWithAccessToken()
    plaid_service = plaid_provider.PlaidProvider(
        http_client=plaid_provider.PlaidHttp(
            token_repository=token_repository, client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET
        ),
        repository=plaid_provider.PlaidRepository(),
    )

    provider_service = Providers({"plaid": plaid_service})

    if action == "INSTITUTIONS_COLLECTION":
        run_async_function_synchronously(plaid_service.collect_institutions)
    elif action == "HISTORICAL_COLLECTION":
        run_async_function_synchronously(
            provider_service.collect_investment_history,
            provider_key="plaid",
            user_id=uuid.UUID("f6b8bdfc-5a9d-11ec-bc23-0242ac1a0002"),
        )
    elif action == "HOLDINGS_COLLECTION":
        run_async_function_synchronously(
            provider_service.collect_current_holdings,
            provider_key="plaid",
            user_id=uuid.UUID("f6b8bdfc-5a9d-11ec-bc23-0242ac1a0002"),
        )
