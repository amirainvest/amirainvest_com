import datetime
from typing import Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import BrokerageJobs, JobsStatus
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_job(session: AsyncSession, job_id: int) -> Optional[BrokerageJobs]:
    response = await session.execute(select(BrokerageJobs).where(BrokerageJobs.id == job_id))
    return response.scalar()


@Session
async def start_job(session: AsyncSession, job_id: int) -> Optional[BrokerageJobs]:
    response = await session.execute(select(BrokerageJobs).where(BrokerageJobs.id == job_id))

    job = response.scalar()
    if job is None:
        return None

    running_jobs_response = await session.execute(
        select(BrokerageJobs).where(
            BrokerageJobs.params == job.params,
            BrokerageJobs.user_id == job.user_id,
            BrokerageJobs.status == JobsStatus.running,
        )
    )

    if len(running_jobs_response.scalars().all()) > 0:
        return None

    await session.execute(update(BrokerageJobs).where(BrokerageJobs.id == job_id).values(status=JobsStatus.running))

    return job


@Session
async def add_job(session: AsyncSession, user_id: str, params: Optional[dict]) -> BrokerageJobs:
    job = BrokerageJobs(
        user_id=user_id,
        status=JobsStatus.pending,
        retries=0,
        params=params,
    )

    session.add(job)
    await session.flush()
    await session.refresh(job)
    return job


@Session
async def end_job(session: AsyncSession, job_id: int, job_status: JobsStatus, error: Optional[str]):
    data = await session.execute(select(BrokerageJobs).where(BrokerageJobs.id == job_id))
    job = data.scalar()
    if job is None:
        return

    retries = job.retries + 1
    await session.execute(
        update(BrokerageJobs)
        .where(BrokerageJobs.id == job_id)
        .values(retries=retries, status=job_status, error=error, ended_at=datetime.datetime.utcnow())
    )
