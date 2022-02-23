import asyncio

from data_imports_amirainvest_com.controllers.data_loader import load_platform_user_data
from data_imports_amirainvest_com.sqs.sqs_pydantic_models import SQSDataLoad


async def run(event: dict):
    data = SQSDataLoad.parse_raw(event["Records"][0])
    await load_platform_user_data(data=data)


def handler(event: dict, context):
    asyncio.run(run(event))
