from brokerage_amirainvest_com.brokerages import plaid_provider
from brokerage_amirainvest_com.dynamo import TokenProvider
from brokerage_amirainvest_com.providers import Providers
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from common_amirainvest_com.utils.consts import PLAID_CLIENT_ID, PLAID_SECRET


user_id = "f6b8bdfc-5a9d-11ec-bc23-0242ac1a0002"
brokerage_item_id = "1M053jRjN0Ugqo0NjxrKsAe4b8OOxXHm4Q3y9"
action = "COLLECT_HOLDINGS"
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
    elif action == "COLLECT_INVESTMENT_HISTORY":
        run_async_function_synchronously(
            provider_service.collect_investment_history,
            provider_key="plaid",
            user_id=user_id,
            item_id=brokerage_item_id,
            job_id=None,
        )
    elif action == "COLLECT_HOLDINGS":
        run_async_function_synchronously(
            provider_service.collect_current_holdings,
            provider_key="plaid",
            user_id=user_id,
            item_id=brokerage_item_id,
            job_id=None,
        )
