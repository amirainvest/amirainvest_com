import json
from typing import List

from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from common_amirainvest_com.utils.logger import log
from data_imports_amirainvest_com.constants import MEDIA_PLATFORM_DATA_LOAD_QUEUE
from data_imports_amirainvest_com.controllers import substack_users, twitter_users, youtubers
from data_imports_amirainvest_com.sqs.sqs_utils import add_message_to_queue


async def get_refresh_ready_platform_data() -> List[tuple]:
    log.info("Getting refresh ready platform data")
    data = []
    all_twitter_users = await twitter_users.get_all_twitter_users()
    all_youtubers = await youtubers.get_all_youtubers()
    all_substack_users = await substack_users.get_all_substack_users()
    data.extend([("twitter", x.twitter_id) for x in all_twitter_users])
    data.extend([("youtube", x.channel_id) for x in all_youtubers])
    data.extend([("substack", x.username) for x in all_substack_users])
    return data


async def load_refresh_ready_data():
    platform_users = await get_refresh_ready_platform_data()
    for platform, platform_unique_id in platform_users:
        print(platform, platform_unique_id)
        log.info(f"Loading data for user {platform_unique_id} on {platform} into Data Load SQS queue.")
        add_message_to_queue(
            MEDIA_PLATFORM_DATA_LOAD_QUEUE,
            json.dumps({"platform": platform, "platform_unique_id": platform_unique_id}),
        )


if __name__ == "__main__":
    print(run_async_function_synchronously(load_refresh_ready_data))
