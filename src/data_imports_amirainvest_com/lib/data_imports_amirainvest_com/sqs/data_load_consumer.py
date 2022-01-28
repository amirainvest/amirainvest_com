from common_amirainvest_com.sqs.consts import EXPEDITED_MEDIA_PLATFORM_DATA_LOAD_QUEUE, MEDIA_PLATFORM_DATA_LOAD_QUEUE
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from common_amirainvest_com.utils.logger import log
from data_imports_amirainvest_com.controllers.data_loader import load_platform_user_data
from data_imports_amirainvest_com.sqs.sqs_utils import consume_queue


async def consume_data_load_sqs_queue(expedited=False):
    log.info("Consuming Data Load Queue...")
    while True:
        if expedited:
            await consume_queue(EXPEDITED_MEDIA_PLATFORM_DATA_LOAD_QUEUE, load_platform_user_data)
        else:
            await consume_queue(MEDIA_PLATFORM_DATA_LOAD_QUEUE, load_platform_user_data)


if __name__ == "__main__":
    run_async_function_synchronously(consume_data_load_sqs_queue)
