import os


MEDIA_PLATFORM_DATA_LOAD_QUEUE = os.environ.get(
    "MEDIA_PLATFORM_DATA_LOAD_QUEUE_ENV", "https://sqs.us-east-1.amazonaws.com/903791206266/data-imports"
)
EXPEDITED_MEDIA_PLATFORM_DATA_LOAD_QUEUE = os.environ.get(
    "EXPEDITED_MEDIA_PLATFORM_DATA_LOAD_QUEUE_ENV",
    "https://sqs.us-east-1.amazonaws.com/903791206266/expedited-data-imports",
)

REDIS_FEED_FANOUT_SQS_QUEUE = os.environ.get(
    "REDIS_FEED_FANOUT_SQS_QUEUE_ENV",
)
