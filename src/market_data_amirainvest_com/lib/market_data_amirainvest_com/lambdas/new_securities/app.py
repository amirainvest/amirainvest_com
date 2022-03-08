import asyncio

from common_amirainvest_com.utils.consts import async_engine
from common_amirainvest_com.utils.logger import log
from market_data_amirainvest_com.cmds import populate_securities


async def run():
    try:
        await populate_securities.run()
    except Exception as err:
        log.exception(err)
        raise err
    finally:
        await async_engine.dispose()


def handler(event, context):
    asyncio.run(run())

handler()
