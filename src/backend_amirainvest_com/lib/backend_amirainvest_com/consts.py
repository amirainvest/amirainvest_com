from common_amirainvest_com.utils.consts import ENVIRONMENT


__all__ = ["PLAID_WEBHOOK_VERIFY_ENDPOINT"]

plaid_env = "sandbox"
if ENVIRONMENT == "production":
    plaid_env = "production"
elif ENVIRONMENT == "development":
    plaid_env = "development"

PLAID_WEBHOOK_VERIFY_ENDPOINT = f"https://{plaid_env}.plaid.com/webhook_verification_key/get"
