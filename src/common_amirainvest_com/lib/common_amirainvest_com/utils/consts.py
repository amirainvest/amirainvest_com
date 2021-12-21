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

DEBUG = os.environ.get("DEBUG", "true").strip().lower()
ENVIRONMENT = os.environ.get("ENVIRONMENT", "local").strip().lower()

POSTGRES_DATABASE_URL = os.environ.get("POSTGRES_DATABASE_URL_ENV", "postgresql://test:test@postgres/test")

if "asyncpg" not in POSTGRES_DATABASE_URL:
    POSTGRES_DATABASE_URL = POSTGRES_DATABASE_URL.replace("://", "+asyncpg://")

engine = create_async_engine(
    POSTGRES_DATABASE_URL,
    future=True,
    echo=True,
)

async_session = sessionmaker(engine, autoflush=False, autocommit=False, class_=AsyncSession, expire_on_commit=False)

COMMON_ROOT_DIR = os.path.dirname(os.path.abspath(__file__)).split("src/common_amirainvest_com")[0]

WEBCACHE = redis.Redis(host="localhost", port=6379)

MAX_FEED_SIZE = 200
AWS_REGION = "us-east-1"

AUTH0_API_AUDIENCE = ""
AUTH0_CLIENT_ID = ""
AUTH0_CLIENT_SECRET = ""
AUTH0_DOMAIN = ""
