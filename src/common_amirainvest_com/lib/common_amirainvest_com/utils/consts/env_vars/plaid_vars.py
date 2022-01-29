import plaid  # type: ignore

from .general_vars import ENVIRONMENT, Environments
from ..tools import decode_env_var


_plaid_dict = decode_env_var("plaid")
PLAID_CLIENT_ID = _plaid_dict["client_id"]
PLAID_SECRET = _plaid_dict["secret"]
PLAID_APPLICATION_NAME = "amira"  # _plaid_dict["application_name"]
PLAID_ENVIRONMENT = plaid.Environment.Sandbox
# TODO This is a catch all for the time being -- we should change this once we get production credentials attached
if ENVIRONMENT == Environments.prod.value or ENVIRONMENT == Environments.staging.value:
    PLAID_ENVIRONMENT = plaid.Environment.Development
