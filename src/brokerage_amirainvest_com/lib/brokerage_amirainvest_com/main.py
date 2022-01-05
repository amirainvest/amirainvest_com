import uuid

from brokerage_amirainvest_com.brokerages import plaid_provider
from brokerage_amirainvest_com.dynamo import TokenProvider
from brokerage_amirainvest_com.providers import Providers
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from common_amirainvest_com.utils.consts import PLAID_CLIENT_ID, PLAID_SECRET


# TODO Collect Historical Transactions based on item id
# TODO Collect Historical Transactions based on amira user(use all item ids available)
# TODO Collect Holdings based on an item id
# TODO Collect Holdings based on a amira user(use all item ids available

action = "HOLDINGS_COLLECTION"
if __name__ == "__main__":
    token_repository = TokenProvider()

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
            item_id="",
        )
    elif action == "HOLDINGS_COLLECTION":
        run_async_function_synchronously(
            provider_service.collect_current_holdings,
            provider_key="plaid",
            user_id=uuid.UUID("f6b8bdfc-5a9d-11ec-bc23-0242ac1a0002"),
            item_id="",
        )
