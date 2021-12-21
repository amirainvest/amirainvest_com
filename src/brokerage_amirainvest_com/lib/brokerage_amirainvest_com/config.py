import os

import toml


_pyproject_toml = toml.load("pyproject.toml")

VERSION = _pyproject_toml["tool"]["poetry"]["version"]
ENVIRONMENT = os.environ.get("ENVIRONMENT", "local").lower()
SENTRY_URL = os.environ.get("SENTRY_URL_ENV", "fake")

if SENTRY_URL == "fake" and ENVIRONMENT != "local":
    raise EnvironmentError("Sentry URL not set for non local env")
elif SENTRY_URL != "fake":
    import sentry_sdk
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    sentry_sdk.init(
        SENTRY_URL,
        release=VERSION,
        traces_sample_rate=1.0,
        integrations=[SqlalchemyIntegration()],
    )

PLAID_CLIENT_ID: str = os.environ.get("PLAID_CLIENT_ID_ENV", "")
PLAID_SECRET: str = os.environ.get("PLAID_SECRET_ENV", "")
