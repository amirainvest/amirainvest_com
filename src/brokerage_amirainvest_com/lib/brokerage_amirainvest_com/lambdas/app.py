import asyncio
from typing import Optional

from brokerage_amirainvest_com.brokerages import plaid_provider
from brokerage_amirainvest_com.dynamo import TokenProvider
from brokerage_amirainvest_com.providers import Providers
from common_amirainvest_com.sqs.models import Brokerage, BrokerageDataActions, BrokerageDataChange
from common_amirainvest_com.utils.consts import async_engine, PLAID_CLIENT_ID, PLAID_SECRET
from common_amirainvest_com.utils.logger import log


async def holdings_change(
    provider_service: Providers, brokerage: Brokerage, user_id: str, token_identifier: str, job_id: Optional[int]
):
    await provider_service.collect_current_holdings(
        provider_key=brokerage.value, user_id=user_id, item_id=token_identifier, job_id=job_id
    )


async def investments_change(
    provider_service: Providers, brokerage: Brokerage, user_id: str, token_identifier: str, job_id: Optional[int]
):
    await provider_service.collect_investment_history(
        provider_key=brokerage.value, user_id=user_id, item_id=token_identifier, job_id=job_id
    )


async def upsert_brokerage_account(
    provider_service: Providers, brokerage: Brokerage, user_id: str, token_identifier: str, job_id: Optional[int]
):
    await provider_service.collect_current_holdings(
        provider_key=brokerage.value, user_id=user_id, item_id=token_identifier, job_id=job_id
    )
    await provider_service.collect_investment_history(
        provider_key=brokerage.value, user_id=user_id, item_id=token_identifier, job_id=job_id
    )


options = {
    BrokerageDataActions.holdings_change: holdings_change,
    BrokerageDataActions.investments_change: investments_change,
    BrokerageDataActions.upsert_brokerage_account: upsert_brokerage_account,
}


async def run(event):
    try:
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
                lambda_func = options[brokerage_data_change.action]
                await lambda_func(
                    provider_service,
                    brokerage_data_change.brokerage,
                    brokerage_data_change.user_id,
                    brokerage_data_change.token_identifier,
                    brokerage_data_change.job_id,
                )
            except KeyError:
                print("action not supported ", brokerage_data_change.action)
    except Exception as err:
        log.exception(err)
        raise err
    finally:
        await async_engine.dispose


def handler(event, context):
    asyncio.run(run(event))
