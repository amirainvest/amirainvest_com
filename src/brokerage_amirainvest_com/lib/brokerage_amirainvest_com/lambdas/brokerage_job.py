from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import HistoricalJobs, HistoricalJobsStatus
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_pending_jobs(session):
    response = await session.execute(
        select(HistoricalJobs).where(HistoricalJobs.status == HistoricalJobsStatus.pending)
    )

    return response.scalars().all()


# Add to SQS to be re-processed

if __name__ == "__main__":
    print("Hello!")
