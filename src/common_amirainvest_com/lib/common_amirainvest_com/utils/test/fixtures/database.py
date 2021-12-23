import asyncio
import os
import typing

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from alembic import command
from alembic.config import Config
from common_amirainvest_com.utils import consts, decorators
from common_amirainvest_com.utils.consts import COMMON_ROOT_DIR
from common_amirainvest_com.utils.test.fixtures.consts import TEST_DB_URL
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def db_engine() -> typing.AsyncIterable[AsyncEngine]:
    db_root_url = os.path.dirname(TEST_DB_URL)
    normal_db_url = os.path.join(db_root_url, "test")
    test_db_name = os.path.basename(TEST_DB_URL)
    alembic_cfg = Config(os.path.join(COMMON_ROOT_DIR, "alembic.ini"))
    async_test_db_url = TEST_DB_URL
    if "asyncpg" not in TEST_DB_URL:
        async_test_db_url = TEST_DB_URL.replace("://", "+asyncpg://")

    normal_engine: Engine = create_engine(
        normal_db_url,
        future=True,
        echo=False,
    )

    with normal_engine.execution_options(autocommit=True, isolation_level="AUTOCOMMIT").connect() as normal_conn:
        normal_conn.execute(text(f"drop database if exists {test_db_name}"))
        normal_conn.execute(text(f"create database {test_db_name} with owner test"))

    test_engine: Engine = create_engine(
        TEST_DB_URL,
        future=True,
        echo=False,
    )
    with test_engine.connect() as test_conn:
        alembic_cfg.attributes["connection"] = test_conn
        command.upgrade(alembic_cfg, "head")
    test_engine.dispose()

    async_test_engine = create_async_engine(
        async_test_db_url,
        future=True,
        echo=True,
    )
    try:
        yield async_test_engine
    finally:
        await async_test_engine.dispose()
        with normal_engine.execution_options(autocommit=True, isolation_level="AUTOCOMMIT").connect() as normal_conn:
            normal_conn.execute(text(f"drop database if exists {test_db_name}"))
        normal_engine.dispose()


@pytest.fixture(scope="function", autouse=True)
async def session_test(db_engine: AsyncEngine, monkeypatch: pytest.MonkeyPatch) -> typing.AsyncIterable[AsyncSession]:
    connection = await db_engine.connect()
    transaction = await connection.begin_nested()
    session = AsyncSession(
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        bind=connection,
    )
    async_session = sessionmaker(
        connection, autoflush=False, autocommit=False, class_=AsyncSession, expire_on_commit=False
    )
    monkeypatch.setattr(consts, "POSTGRES_DATABASE_URL", str(db_engine.url))
    monkeypatch.setenv("POSTGRES_DATABASE_URL_ENV", str(db_engine.url))

    monkeypatch.setattr(consts, "engine", db_engine)

    monkeypatch.setattr(decorators, "_session", session)
    monkeypatch.setattr(decorators, "_async_session", async_session)

    monkeypatch.setattr(consts, "async_session", async_session)
    await session.begin_nested()

    print("BEFORE SESSION")
    yield session
    print("AFTER SESSION")

    await session.rollback()
    await session.close()
    await transaction.rollback()
    await connection.close()
