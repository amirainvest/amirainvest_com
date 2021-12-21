from typing import List

from common_amirainvest_com.sqs.consts import EXPEDITED_MEDIA_PLATFORM_DATA_LOAD_QUEUE, MEDIA_PLATFORM_DATA_LOAD_QUEUE
from common_amirainvest_com.sqs.models import MediaPlatformDataLoadQueueModel
from common_amirainvest_com.sqs.utils import add_message_to_queue
from common_amirainvest_com.utils.logger import log


def add_data_import_data_to_sqs_queue(data_import: List[dict], expedited: bool = True):
    for data in data_import:
        try:
            message = MediaPlatformDataLoadQueueModel(
                **{
                    "platform": data["platform"],
                    "platform_unique_id": data["unique_platform_id"],
                    "creator_id": data["creator_id"],
                }
            )
            add_message_to_queue(
                MEDIA_PLATFORM_DATA_LOAD_QUEUE if not expedited else EXPEDITED_MEDIA_PLATFORM_DATA_LOAD_QUEUE,
                message=message,
            )
        except Exception as e:
            log.exception(
                f"SQS data load exception: {e} for platform: {data['platform']} id:{data['unique_platform_id']}"
            )
