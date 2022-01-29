import base64
import json
import os


def decode_env_var(env_var_name: str) -> dict:
    env_var_dict = json.loads(base64.b64decode(os.environ.get(env_var_name, "")).decode("utf-8"))
    return env_var_dict


