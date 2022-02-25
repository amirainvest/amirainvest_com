from brokerage_amirainvest_com.brokerages.interfaces import BrokerageInterface
from brokerage_amirainvest_com.jobs import add_job, end_job, get_job, start_job
from common_amirainvest_com.schemas.schema import JobsStatus


def manage_job(fnc):
    async def handle_job(*args, **kwargs):
        job_id = kwargs["job_id"]
        item_id = kwargs["item_id"]
        user_id = kwargs["user_id"]
        provider_key = kwargs["provider_key"]
        func_name = fnc.__name__

        try:
            if job_id is None:
                job = await add_job(user_id, {"item_id": item_id, "provider_key": provider_key, "func": func_name})
            else:
                job = await get_job(job_id)
            job = await start_job(job.id)
        except Exception as err:
            raise err

        try:
            await fnc(args[0], item_id=item_id, user_id=user_id, provider_key=provider_key)
            await end_job(job.id, JobsStatus.succeeded, None)
        except Exception as err:
            await end_job(job.id, JobsStatus.failed, repr(err))
            raise err

    return handle_job


class Providers:
    providers_dict: dict[str, BrokerageInterface]

    def __init__(self, provider_dict: dict[str, BrokerageInterface]):
        self.providers_dict = provider_dict

    @manage_job
    async def collect_institutions(self, provider_key: str, user_id: str, item_id: str):
        pass
        # try:
        #     # provider = self.providers_dict[provider_key]
        #     # provider.__class__ = plaid_provider.PlaidProvider
        #     # await provider.collect_institutions()
        # except Exception as err:
        #     raise err

    @manage_job
    async def collect_investment_history(self, provider_key: str, user_id: str, item_id: str):
        try:
            provider = self.providers_dict[provider_key]
            await provider.collect_investment_history(user_id=user_id, item_id=item_id)
        except Exception as err:
            raise err

    @manage_job
    async def collect_current_holdings(self, provider_key: str, user_id: str, item_id: str):
        try:
            provider = self.providers_dict[provider_key]
            await provider.collect_current_holdings(user_id=user_id, item_id=item_id)
        except Exception as err:
            raise err

    @manage_job
    async def compute_holdings_history(self, provider_key: str, user_id: str, item_id: str):
        try:
            provider = self.providers_dict[provider_key]
            await provider.compute_holdings_history(user_id=user_id, item_id=item_id)
        except Exception as err:
            raise err
