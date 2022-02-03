import pytest
from sqlalchemy.orm import sessionmaker

from common_amirainvest_com.schemas.schema import Base
from common_amirainvest_com.utils.test.factories.postgres_factories import Factories


@pytest.fixture(scope="function", autouse=True)
async def factory(async_session_maker_test: sessionmaker) -> Factories:
    factory = Factories(async_session_maker=async_session_maker_test, base=Base)
    return factory
