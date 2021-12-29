import os


PLAID_CLIENT_ID: str = os.environ.get("PLAID_CLIENT_ID_ENV", "")
PLAID_SECRET: str = os.environ.get("PLAID_SECRET_ENV", "")
