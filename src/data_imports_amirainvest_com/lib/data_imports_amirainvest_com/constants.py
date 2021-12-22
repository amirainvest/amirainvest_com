import os


MEDIA_PLATFORM_DATA_LOAD_QUEUE = "https://sqs.us-east-1.amazonaws.com/903791206266/data-imports"
EXPEDITED_MEDIA_PLATFORM_DATA_LOAD_QUEUE = "https://sqs.us-east-1.amazonaws.com/903791206266/expedited-data-imports"

REDIS_FEED_FANOUT_SQS_QUEUE = ""

TWITTER_API_TOKEN_ENV = os.environ.get(
    "TWITTER_API_TOKEN_ENV",
    "AAAAAAAAAAAAAAAAAAAAAEX6RgEAAAAAPeK0DFITauB2h7o8PeESVRt1WEs%3DpR3LqglpLKmd1FbhAGyWFACEuMOoYMkVAqJSlz851opBTB1fOI",
)
STRIPE_API_KEY_ENV = os.environ.get(
    "STRIPE_API_KEY_ENV",
    "sk_test_51JvusJDh18jbQ66oYHUGV0kxQiPOC9vMHnSX2KCEsjwKCErSjmOcZI5dFLttH1RLIiBX4B1P6ZS52lPcAueWDgfr00ms76rb5r",
)
YOUTUBE_API_KEY_ENV = os.environ.get("YOUTUBE_API_KEY_ENV", "AIzaSyBkwVzrf3N7a92QgIQ4WMijyAQ6CaQQp9c")
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"
TWITTER_API_URL = "https://api.twitter.com"
AWS_REGION = "us-west-2"
LOCAL_POSTGRES = "postgres://test:test@localhost:5432/test"
