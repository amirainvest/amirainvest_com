import asyncio

from brokerage_amirainvest_com.brokerages import plaid_provider
from brokerage_amirainvest_com.dynamo import TokenProvider
from brokerage_amirainvest_com.providers import Providers
from common_amirainvest_com.utils.consts import PLAID_CLIENT_ID, PLAID_SECRET


user_id = "fbf26e93-30f1-4e0b-8a28-df1791bbb42e"
brokerage_item_id = "N0dXX1LRbBF0gkNZAyOyUPw0zKm5r1fRj4eP0"
action = "COLLECT_INVESTMENT_HISTORY"
if __name__ == "__main__":
    token_repository = TokenProvider()
    plaid_http = plaid_provider.PlaidHttp(
        token_repository=token_repository, client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET
    )
    plaid_service = plaid_provider.PlaidProvider(
        http_client=plaid_http,
        repository=plaid_provider.PlaidRepository(),
    )

    provider_service = Providers({"plaid": plaid_service})

    if action == "INSTITUTIONS_COLLECTION":
        asyncio.run(plaid_service.collect_institutions())
    elif action == "COLLECT_INVESTMENT_HISTORY":
        asyncio.run(
            provider_service.collect_investment_history(
                provider_key="plaid", user_id=user_id, item_id=brokerage_item_id, job_id=None
            )
        )
    elif action == "COLLECT_HOLDINGS":
        asyncio.run(
            provider_service.collect_current_holdings(
                provider_key="plaid", user_id=user_id, item_id=brokerage_item_id, job_id=None
            )
        )
    elif action == "COMPUTE_HOLDINGS_HISTORY":
        asyncio.run(
            provider_service.compute_holdings_history(
                provider_service="plaid", user_id=user_id, item_id=brokerage_item_id, job_id=None
            )
        )
