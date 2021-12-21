from typing import Iterator

from sqlalchemy.ext.asyncio import AsyncSession

from common_amirainvest_com.utils.consts import async_session


def async_session_instance() -> Iterator[AsyncSession]:
    session: AsyncSession
    async with async_session() as session:
        async with session.begin():
            yield session
