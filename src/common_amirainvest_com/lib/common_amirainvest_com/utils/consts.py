import base64
import json
import os
from enum import Enum
from json import JSONDecodeError

import plaid  # type: ignore
import redis
import sentry_sdk
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.utils import BadDsn
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


__all__ = [
    "decode_env_var",
    "DEBUG",
    "Environments",
    "ENVIRONMENT",
    "async_session_maker",
    "COMMON_ROOT_DIR",
    "AWS_REGION",
    "MAX_FEED_SIZE",
    "AUTH0_CLIENT_ID",
    "AUTH0_CLIENT_SECRET",
    "AUTH0_DOMAIN",
    "AUTH0_API_AUDIENCE",
    "WEBCACHE",
    "PLAID_CLIENT_ID",
    "PLAID_SECRET",
    "PLAID_APPLICATION_NAME",
    "PLAID_ENVIRONMENT",
    "IEX_URL",
    "IEX_PUBLISHABLE",
    "IEX_SECRET",
]


class Environments(Enum):
    prod = "prod"
    staging = "staging"
    local = "local"


class Projects(Enum):
    mono = "mono"
    backend = "backend"
    brokerage = "brokerage"
    market_data = "market_data"


def decode_env_var(env_var_name: str) -> dict:
    env_var_dict = json.loads(base64.b64decode(os.environ.get(env_var_name, "")).decode("utf-8"))
    return env_var_dict


DEBUG = os.environ.get("DEBUG", "true").strip().lower()
ENVIRONMENT = Environments[os.environ.get("ENVIRONMENT", "local").strip().lower()].value
PROJECT = Projects[os.environ.get("PROJECT", "mono").strip().lower()].value

try:
    integrations = [SqlalchemyIntegration(), RedisIntegration()]

    if PROJECT == "brokerage" or PROJECT == "market_data":
        from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration


        integrations.append(AwsLambdaIntegration(timeout_warning=True))

    SENTRY_URL = "https://{public_key}@{domain}/{project_id}".format(**decode_env_var("sentry"))

    sentry_sdk.init(
        SENTRY_URL,
        environment=ENVIRONMENT,
        sample_rate=1.0,
        traces_sample_rate=1.0,
        request_bodies="always",
        integrations=integrations,
        debug=True if DEBUG == "true" else False,
    )
except (BadDsn, JSONDecodeError):
    if ENVIRONMENT != Environments.local.value:
        raise EnvironmentError("Sentry URL not set for non local env")

POSTGRES_DATABASE_URL = "postgresql://{username}:{password}@{host}/{database}".format(**decode_env_var("postgres"))

WEBCACHE_DICT = decode_env_var("webcache")

MAX_FEED_SIZE = 200
AWS_REGION = "us-east-1"

_auth0_dict = decode_env_var("auth0")
AUTH0_API_AUDIENCE = _auth0_dict["api_audience"]
AUTH0_CLIENT_ID = _auth0_dict["client_id"]
AUTH0_CLIENT_SECRET = _auth0_dict["client_secret"]
AUTH0_DOMAIN = _auth0_dict["domain"]

_auth0_management_dict = decode_env_var("auth0_management")
AUTH0_MANAGEMENT_API_AUDIENCE = _auth0_management_dict["api_audience"]
AUTH0_MANAGEMENT_CLIENT_ID = _auth0_management_dict["client_id"]
AUTH0_MANAGEMENT_CLIENT_SECRET = _auth0_management_dict["client_secret"]
AUTH0_MANAGEMENT_DOMAIN = _auth0_management_dict["domain"]

_plaid_dict = decode_env_var("plaid")
PLAID_CLIENT_ID = _plaid_dict["client_id"]
PLAID_SECRET = _plaid_dict["secret"]
PLAID_APPLICATION_NAME = "amira"  # _plaid_dict["application_name"]
PLAID_ENVIRONMENT = plaid.Environment.Sandbox
# TODO This is a catch all for the time being -- we should change this once we get production credentials attached
if ENVIRONMENT == Environments.prod.value or ENVIRONMENT == Environments.staging.value:
    PLAID_ENVIRONMENT = plaid.Environment.Development

_iex_dict = decode_env_var("iex")
IEX_PUBLISHABLE = _iex_dict["publishable"]
IEX_SECRET = _iex_dict["secret"]
IEX_URL = "https://sandbox.iexapis.com/stable"
if ENVIRONMENT == Environments.staging.value or ENVIRONMENT == Environments.prod.value:
    IEX_URL = "https://cloud.iexapis.com/stable"

COMMON_ROOT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src/common_amirainvest_com")[0]

if "asyncpg" not in POSTGRES_DATABASE_URL:
    POSTGRES_DATABASE_URL = POSTGRES_DATABASE_URL.replace("://", "+asyncpg://")

async_engine = create_async_engine(
    POSTGRES_DATABASE_URL,
    future=True,
    echo=True,
)

async_session_maker = sessionmaker(
    async_engine,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True,
)

# https://github.com/redis/redis-py
_redis_connection_pool = redis.ConnectionPool(**WEBCACHE_DICT)
WEBCACHE = redis.Redis(connection_pool=_redis_connection_pool, health_check_interval=30)

if __name__ == "__main__":
    print(decode_env_var("brokerages"))
