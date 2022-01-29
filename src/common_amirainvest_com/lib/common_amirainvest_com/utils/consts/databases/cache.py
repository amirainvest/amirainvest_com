import redis

from ..tools import decode_env_var


WEBCACHE_DICT = decode_env_var("webcache")
# https://github.com/redis/redis-py
WEBCACHE = redis.Redis(health_check_interval=30, ssl=True, ssl_cert_reqs=None, **WEBCACHE_DICT)
