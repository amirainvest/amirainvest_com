import asyncio

from sqlalchemy import select

from common_amirainvest_com.schemas.schema import ChipLabels, Securities, TradingStrategies
from common_amirainvest_com.utils.decorators import Session


@Session
async def get_trading_strategies(session):
    return (await session.execute(select(TradingStrategies.name))).scalars().all()


@Session
async def get_benchmarks(session):
    benchmarks = (
        (await session.execute(select(Securities).where(Securities.is_benchmark == True))).scalars().all()  # noqa: E712
    )
    return [{"id": x.id, "benchmark": x.human_readable_name} for x in benchmarks]


@Session
async def get_chip_labels(session):
    return (await session.execute(select(ChipLabels.name))).scalars().all()


async def get_config():
    chip_labels, benchmarks, trading_strategies = await asyncio.gather(
        get_chip_labels(), get_benchmarks(), get_trading_strategies()
    )
    return {"chip_labels": chip_labels, "benchmarks": benchmarks, "trading_strategies": trading_strategies}
