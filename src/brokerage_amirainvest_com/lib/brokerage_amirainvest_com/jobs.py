import datetime
import uuid
from typing import Optional

from sqlalchemy import and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import FinancialJobs, FinancialJobsStatus
from common_amirainvest_com.utils.decorators import Session


MAX_JOB_RETRIES = 3


# TODO: We should set a composite index on User,Running, & Params and if insert fails, then return id
#   rather than selecting, then inserting -- as this could be a concurrency issue, or we could
#   do something like lock table for each transaction
@Session
async def start_historical_job(session: AsyncSession, user_id: uuid.UUID) -> Optional[int]:
    response = await session.execute(
        select(FinancialJobs).where(
            and_(FinancialJobs.user_id == user_id),
            and_(FinancialJobs.status == FinancialJobsStatus.running),
        )
    )

    data = response.scalars().all()
    if len(data) > 0:
        return 0

    historical_job = FinancialJobs(
        user_id=user_id,
        status=FinancialJobsStatus.running,
        retries=0,
        params="",
        started_at=datetime.datetime.utcnow(),
    )

    session.add(historical_job)
    await session.flush()
    await session.refresh(historical_job)
    return historical_job.id


@Session
async def end_historical_job(session: AsyncSession, job_id: int, status: FinancialJobsStatus):
    return await session.execute(
        update(FinancialJobs)
        .where(FinancialJobs.id == job_id)
        .values(status=status, ended_at=datetime.datetime.utcnow())
    )


async def end_historical_job_successfully(job_id: int):
    return await end_historical_job(job_id, FinancialJobsStatus.succeeded)


@Session
async def retry_historical_job(session: AsyncSession, job_id: int):
    data = await session.execute(select(FinancialJobs).where(FinancialJobs.id == job_id))
    job = data.scalar()
    if job is None:
        return
    if job.retries > MAX_JOB_RETRIES:
        return await end_historical_job(job_id=job_id, status=FinancialJobsStatus.failed)

    cur_retires = job.retries + 1
    return await session.execute(
        update(FinancialJobs)
        .where(FinancialJobs.id == job_id)
        .values(retries=cur_retires, status=FinancialJobsStatus.pending)
    )
