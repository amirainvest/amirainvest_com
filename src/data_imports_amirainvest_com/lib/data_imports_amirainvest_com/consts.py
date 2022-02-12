from common_amirainvest_com.utils.consts import decode_env_var


_twitter_dict = decode_env_var("twitter")
TWITTER_API_TOKEN_ENV = _twitter_dict["api_token"]
TWITTER_API_URL = _twitter_dict["url"]

# _stripe_dict = decode_env_var("stripe")
# STRIPE_API_KEY_ENV = _stripe_dict["api_key"]

_youtube_dict = decode_env_var("youtube")
YOUTUBE_API_KEY_ENV = _youtube_dict["api_key"]
YOUTUBE_API_URL = _youtube_dict["url"]
