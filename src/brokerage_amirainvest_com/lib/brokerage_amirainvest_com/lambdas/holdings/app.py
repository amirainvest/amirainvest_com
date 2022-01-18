from uuid import UUID

from brokerage_amirainvest_com.brokerages import plaid_provider
from brokerage_amirainvest_com.dynamo import TokenProvider
from brokerage_amirainvest_com.providers import Providers
from common_amirainvest_com.sqs.models import Brokerage, BrokerageDataChange
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from common_amirainvest_com.utils.consts import PLAID_CLIENT_ID, PLAID_SECRET


async def holdings_change(provider_service: Providers, brokerage: Brokerage, user_id: str, token_identifier: str):
    await provider_service.collect_current_holdings(
        provider_key=brokerage.value, user_id=UUID(user_id), item_id=token_identifier
    )


def handler(event, context):
    token_repository = TokenProvider()
    plaid_service = plaid_provider.PlaidProvider(
        http_client=plaid_provider.PlaidHttp(
            token_repository=token_repository, client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET
        ),
        repository=plaid_provider.PlaidRepository(),
    )

    provider_service = Providers({"plaid": plaid_service})
    for record in event["Records"]:
        brokerage_data_change = BrokerageDataChange.parse_raw(record["body"])
        try:
            func = holdings_change
            run_async_function_synchronously(
                func,
                provider_service,
                brokerage_data_change.brokerage,
                brokerage_data_change.user_id,
                brokerage_data_change.token_identifier,
            )
        except KeyError:
            print("action not supported ", brokerage_data_change.action)
