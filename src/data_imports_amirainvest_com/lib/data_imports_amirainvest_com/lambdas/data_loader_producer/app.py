import asyncio

from data_imports_amirainvest_com.sqs.data_load_producer import load_refresh_ready_data


async def run():
    await load_refresh_ready_data()


def handler(event: dict, context):
    asyncio.run(run())
