import base64
import json
import os

import redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


__all__ = [
    "DEBUG",
    "ENVIRONMENT",
    "async_session",
    "COMMON_ROOT_DIR",
    "AWS_REGION",
    "MAX_FEED_SIZE",
    "AUTH0_CLIENT_ID",
    "AUTH0_CLIENT_SECRET",
    "AUTH0_DOMAIN",
    "AUTH0_API_AUDIENCE",
    "WEBCACHE",
]


def _decode_env_var(env_var_name: str) -> dict:
    _postgres_url_dict = json.loads(base64.b64decode(os.environ.get(env_var_name)).decode("utf-8"))
    return _postgres_url_dict


DEBUG = os.environ.get("DEBUG", "true").strip().lower()
ENVIRONMENT = os.environ.get("ENVIRONMENT", "local").strip().lower()

POSTGRES_DATABASE_URL = "postgresql://{username}:{password}@{host}/{database}".format(**_decode_env_var("postgres"))

WEBCACHE_URL = _decode_env_var("webcache")

MAX_FEED_SIZE = 200
AWS_REGION = "us-east-1"

_auth0_dict = _decode_env_var("auth0")
AUTH0_API_AUDIENCE = ""
AUTH0_CLIENT_ID = _auth0_dict["client_id"]
AUTH0_CLIENT_SECRET = _auth0_dict["client_secret"]
AUTH0_DOMAIN = _auth0_dict["domain"]

COMMON_ROOT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src/common_amirainvest_com")[0]

if "asyncpg" not in POSTGRES_DATABASE_URL:
    POSTGRES_DATABASE_URL = POSTGRES_DATABASE_URL.replace("://", "+asyncpg://")

engine = create_async_engine(
    POSTGRES_DATABASE_URL,
    future=True,
    echo=True,
)

async_session = sessionmaker(engine, autoflush=False, autocommit=False, class_=AsyncSession, expire_on_commit=False)
WEBCACHE = redis.Redis(host="localhost", port=6379)
