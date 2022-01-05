import uuid

from brokerage_amirainvest_com.brokerages.brokerage_interface import BrokerageInterface
from brokerage_amirainvest_com.jobs import end_historical_job_successfully, retry_historical_job, start_historical_job


class Providers:
    providers_dict: dict[str, BrokerageInterface]

    def __init__(self, provider_dict: dict[str, BrokerageInterface]):
        self.providers_dict = provider_dict

    # TODO: How can we degrade this gracefully, if we stop the service?
    async def collect_investment_history(self, provider_key: str, user_id: uuid.UUID):
        provider = self.providers_dict[provider_key]
        job_id = await start_historical_job(user_id)

        # Job has already started
        if job_id == 0:
            return

        # TODO: Maybe we return a bad response if we are unable to perform the action?? Or we throw
        #   an exception?
        try:
            await provider.collect_investment_history(user_id=user_id)
            await end_historical_job_successfully(job_id)
        except Exception:
            await retry_historical_job(job_id)

    async def collect_current_holdings(self, provider_key: str, user_id: uuid.UUID):
        provider = self.providers_dict[provider_key]
        await provider.collect_current_holdings(user_id=user_id)
