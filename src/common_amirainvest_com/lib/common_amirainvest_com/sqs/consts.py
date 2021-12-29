from common_amirainvest_com.utils.consts import decode_env_var, ENVIRONMENT


_sqs_dict = decode_env_var("sqs")
MEDIA_PLATFORM_DATA_LOAD_QUEUE = f"{_sqs_dict['url']}/{ENVIRONMENT}-data-imports"
EXPEDITED_MEDIA_PLATFORM_DATA_LOAD_QUEUE = f"{_sqs_dict['url']}/{ENVIRONMENT}-expedited-data-imports"

REDIS_FEED_FANOUT_SQS_QUEUE = f"{_sqs_dict['url']}/{ENVIRONMENT}-redis-feed"
