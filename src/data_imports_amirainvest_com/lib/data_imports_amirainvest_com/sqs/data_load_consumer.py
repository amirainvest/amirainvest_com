from common_amirainvest_com.sqs.consts import EXPEDITED_MEDIA_PLATFORM_DATA_LOAD_QUEUE, MEDIA_PLATFORM_DATA_LOAD_QUEUE
from common_amirainvest_com.utils.logger import log
from data_imports_amirainvest_com.controllers.data_loader import load_platform_user_data
from data_imports_amirainvest_com.sqs.sqs_utils import consume_queue


def consume_data_load_sqs_queue(expedited=False):
    log.info("Consuming Data Load Queue...")
    while True:
        if expedited:
            consume_queue(EXPEDITED_MEDIA_PLATFORM_DATA_LOAD_QUEUE, load_platform_user_data)
        else:
            consume_queue(MEDIA_PLATFORM_DATA_LOAD_QUEUE, load_platform_user_data)
