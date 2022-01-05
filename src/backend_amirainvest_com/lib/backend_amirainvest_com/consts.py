from plaid import Environment  # type: ignore

from common_amirainvest_com.utils.consts import ENVIRONMENT, Environments


__all__ = ["PLAID_ENVIRONMENT"]

PLAID_ENVIRONMENT = Environment.Sandbox
if ENVIRONMENT == Environments.prod.value:
    PLAID_ENVIRONMENT = Environment.Production
elif ENVIRONMENT == Environments.staging.value:
    PLAID_ENVIRONMENT = Environment.Development
