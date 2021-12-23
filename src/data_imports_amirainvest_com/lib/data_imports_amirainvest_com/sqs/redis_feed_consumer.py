import json

from common_amirainvest_com.utils.consts import WEBCACHE
from data_imports_amirainvest_com.constants import REDIS_FEED_FANOUT_SQS_QUEUE
from data_imports_amirainvest_com.sqs.sqs_utils import consume_queue


PAGE_SIZE = 30
MAX_HOURS_AGO = 168
MAX_FEED_SIZE = 200


def add_post_to_redis_feed(user_id: str, post: dict, feed_type: str, max_feed_size: int = MAX_FEED_SIZE):
    key = f"{user_id}-{feed_type}"
    WEBCACHE.lpush(key, json.dumps(post))
    WEBCACHE.ltrim(key, 0, max_feed_size)


def consume_redis_feed_sqs_queue():
    consume_queue(REDIS_FEED_FANOUT_SQS_QUEUE, add_post_to_redis_feed)
