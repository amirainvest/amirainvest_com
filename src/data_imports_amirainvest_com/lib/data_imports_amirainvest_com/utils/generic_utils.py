import hashlib

from common_amirainvest_com.utils.logger import log


def hash_string(string: str):
    log.info(f"Hashing {string}")
    return hashlib.md5(string.encode()).hexdigest()
