import base64

from Crypto import Random
from Crypto.Hash import SHA256


def clean_string(string: str) -> str:
    return string.replace("=", "").replace("+", "-").replace("/", "_")


class CodeChallenge(object):
    def __init__(self):
        self.verify = clean_string(base64.urlsafe_b64encode(Random.get_random_bytes(32)).decode("ascii"))
        self.challenge = self.make_challenge()

    def make_challenge(self, verify=None):
        if not verify:
            verify = self.verify
        sha = SHA256.new()
        sha.update(bytes(verify, "ascii"))
        return clean_string(base64.urlsafe_b64encode(sha.digest()).decode("ascii"))
