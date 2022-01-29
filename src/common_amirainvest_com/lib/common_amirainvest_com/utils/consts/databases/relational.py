import typing as t

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..tools import decode_env_var
from ...async_utils import run_async_function_synchronously


POSTGRES_DATABASE_URL = "postgresql://{username}:{password}@{host}/{database}".format(**decode_env_var("postgres"))
if "asyncpg" not in POSTGRES_DATABASE_URL:
    POSTGRES_DATABASE_URL = POSTGRES_DATABASE_URL.replace("://", "+asyncpg://")


# async def async_teardown():
#     try:
#         await async_engine.dispose()
#     except NameError:
#         pass
#
#
# async def async_setup():
#     global async_engine
#     global async_session_maker
#
#     await async_teardown()
#
#     async_engine = create_async_engine(
#         POSTGRES_DATABASE_URL,
#         future=True,
#         echo=True,
#     )
#     async_session_maker = sessionmaker(
#         async_engine,
#         autoflush=False,
#         autocommit=False,
#         class_=AsyncSession,
#         expire_on_commit=False,
#         future=True,
#     )


# run_async_function_synchronously(async_setup)

# async_engine: AsyncEngine
# async_session_maker: t.Callable[[], AsyncSession]

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
