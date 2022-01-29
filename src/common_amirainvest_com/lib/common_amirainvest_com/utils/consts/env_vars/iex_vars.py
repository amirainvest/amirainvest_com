from .general_vars import ENVIRONMENT, Environments
from ..tools import decode_env_var


_iex_dict = decode_env_var("iex")
IEX_PUBLISHABLE = _iex_dict["publishable"]
IEX_SECRET = _iex_dict["secret"]
IEX_URL = "https://sandbox.iexapis.com/stable"
if ENVIRONMENT == Environments.staging.value or ENVIRONMENT == Environments.prod.value:
    IEX_URL = "https://cloud.iexapis.com/stable"
