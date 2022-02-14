from common_amirainvest_com.utils.consts import decode_env_var, ENVIRONMENT


_sqs_dict = decode_env_var("sqs")
MEDIA_PLATFORM_DATA_LOAD_QUEUE = f"{_sqs_dict['url']}/{ENVIRONMENT}-data-imports"
EXPEDITED_MEDIA_PLATFORM_DATA_LOAD_QUEUE = f"{_sqs_dict['url']}/{ENVIRONMENT}-expedited-data-imports"
BROKERAGE_DATA_QUEUE_URL = f"{_sqs_dict['url']}/{ENVIRONMENT}-brokerage-data"
