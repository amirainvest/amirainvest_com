import asyncio
import json

from data_imports_amirainvest_com.controllers.data_loader import load_platform_user_data
from data_imports_amirainvest_com.sqs.sqs_pydantic_models import SQSDataLoad


async def run(event: dict):
    data = SQSDataLoad.parse_raw(json.dumps(event["Records"][0]))
    await load_platform_user_data(data=data)


def handler(event: dict, context):
    asyncio.run(run(event))


# if __name__ == '__main__':
#     event = {'Records':[{"platform": "substack", "platform_unique_id": "tanay",
#  "creator_id": "77ba34ef-5472-4ca1-9f70-4dacb98ebed0"}]}
#     asyncio.run(run(event))
