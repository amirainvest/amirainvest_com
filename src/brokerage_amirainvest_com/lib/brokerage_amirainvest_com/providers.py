from typing import Optional

from brokerage_amirainvest_com.brokerages.interfaces import BrokerageInterface
from brokerage_amirainvest_com.jobs import add_job, end_job, get_job, start_job
from common_amirainvest_com.schemas.schema import BrokerageJobs, JobsStatus


async def handle_job(job_id: Optional[int], user_id: str, item_id: str, provider_key: str, func: str) -> Optional[
    BrokerageJobs]:
    try:
        if job_id is None:
            job = await add_job(
                user_id, {"item_id": item_id, "provider_key": provider_key, "func": func}
            )
        else:
            job = await get_job(job_id)
        return await start_job(job.id)
    except Exception as err:
        raise err


class Providers:
    providers_dict: dict[str, BrokerageInterface]

    def __init__(self, provider_dict: dict[str, BrokerageInterface]):
        self.providers_dict = provider_dict

    async def collect_investment_history(self, provider_key: str, user_id: str, item_id: str, job_id: Optional[int]):
        try:
            job = await handle_job(
                job_id=job_id, user_id=user_id, item_id=item_id, provider_key=provider_key,
                func="collect_investment_history"
            )
            if job is None:
                return
        except Exception as err:
            raise err

        try:
            provider = self.providers_dict[provider_key]
            await provider.collect_investment_history(user_id=user_id, item_id=item_id)
            await end_job(job.id, JobsStatus.succeeded, None)
        except Exception as err:
            await end_job(job.id, JobsStatus.failed, repr(err))

    async def collect_current_holdings(self, provider_key: str, user_id: str, item_id: str, job_id: Optional[int]):
        try:
            job = await handle_job(
                job_id=job_id, user_id=user_id, item_id=item_id, provider_key=provider_key,
                func="collect_current_holdings"
            )
            if job is None:
                return
        except Exception as err:
            raise err

        try:
            provider = self.providers_dict[provider_key]
            await provider.collect_current_holdings(user_id=user_id, item_id=item_id)
            await end_job(job.id, JobsStatus.succeeded, None)
        except Exception as err:
            await end_job(job.id, JobsStatus.failed, repr(err))
