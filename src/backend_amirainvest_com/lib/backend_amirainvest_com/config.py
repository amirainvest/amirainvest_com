import os

import toml


_pyproject_toml = toml.load("pyproject.toml")

VERSION = _pyproject_toml["tool"]["poetry"]["version"]
ENVIRONMENT = os.environ.get("ENVIRONMENT", "local").lower()
SENTRY_URL = os.environ.get("SENTRY_URL_ENV", "fake")
print(ENVIRONMENT)

DATA_IMPORTS_API_URL = "https://dataimports.amirainvest.com"
BROKERAGE_DATA_QUEUE_URL = "http://localhost:9324/queue/default"

if SENTRY_URL == "fake" and ENVIRONMENT != "local":
    raise EnvironmentError("Sentry URL not set for non local env")
elif SENTRY_URL != "fake":
    print(SENTRY_URL)
    import sentry_sdk
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    sentry_sdk.init(
        SENTRY_URL,
        release=VERSION,
        traces_sample_rate=1.0,
        integrations=[SqlalchemyIntegration()],
    )

TEST_URL = "TEST"
