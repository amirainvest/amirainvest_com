import json
from typing import List, Tuple

from common_amirainvest_com.sqs.consts import MEDIA_PLATFORM_DATA_LOAD_QUEUE
from common_amirainvest_com.utils.logger import log
from data_imports_amirainvest_com.controllers import substack_users, twitter_users, youtubers
from data_imports_amirainvest_com.sqs.sqs_utils import add_message_to_queue


async def get_refresh_ready_platform_data() -> List[Tuple[str, str, str]]:
    log.info("Getting refresh ready platform data")
    data = []
    all_twitter_users = await twitter_users.get_all_twitter_users()
    all_youtubers = await youtubers.get_all_youtubers()
    all_substack_users = await substack_users.get_all_substack_users()
    data.extend([("twitter", x.twitter_user_id, str(x.creator_id)) for x in all_twitter_users])
    data.extend([("youtube", x.channel_id, str(x.creator_id)) for x in all_youtubers])
    data.extend([("substack", x.username, str(x.creator_id)) for x in all_substack_users])
    return data


async def load_refresh_ready_data():
    platform_users = await get_refresh_ready_platform_data()
    for platform, platform_unique_id, creator_id in platform_users:
        log.info(
            f"Loading data for user {creator_id} {platform_unique_id} on {platform} into media data load SQS queue."
        )
        add_message_to_queue(
            MEDIA_PLATFORM_DATA_LOAD_QUEUE,
            json.dumps({"platform": platform, "platform_unique_id": platform_unique_id, "creator_id": creator_id}),
        )
