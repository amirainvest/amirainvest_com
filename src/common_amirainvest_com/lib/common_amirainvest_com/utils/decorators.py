import functools
import inspect
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from common_amirainvest_com.utils.consts import async_session_maker
from common_amirainvest_com.utils.logger import log


__all__ = ["Session", "get_async_session"]
_async_session: Optional[AsyncSession] = None  # NOTE: This is monkeypatched by a test fixture!
_async_session_maker = async_session_maker  # NOTE: This is monkeypatched by a test fixture!


# TODO add typing for session decorator
#   Waiting on : https://github.com/python/mypy/pull/11847
#   and https://github.com/python/mypy/issues/11833


def get_async_session() -> Optional[AsyncSession]:
    """
    Used by the test factories to get the session at factory run time.
    """
    return _async_session


def Session(func):
    """
    Decorator that adds a SQLAlchemy AsyncSession to the function passed if the function is not
    already being passed an AsyncSession object.

    If no AsyncSession object is being passes this decorator will handle all session commit and
    rollback operations. Commit if no errors, rollback if there is an error raised.

    Example:

    @Session
    async def example(session: AsyncSession, other_data: str):
        ...

    a = await example(other_data="stuff")
    b = await example(async_session_maker(), "stuff")


    NOTE: The FIRST or SECOND argument is "session". "session" in ANY OTHER ARGUMENT SPOT will break!
    ONLY pass an AsyncSession object or NOTHING to the "session" argument!
    """

    async def _session_work(session: AsyncSession, args, kwargs):
        if "session" in kwargs:
            kwargs["session"] = session
        elif "session" in list(inspect.signature(func).parameters.keys()):
            sig_args = list(inspect.signature(func).parameters.keys())
            if sig_args[0] == "session":
                args = (session, *args)
            elif sig_args[0] in {"cls", "self"} and sig_args[1] == "session":
                args = (args[0], session, *args[1:])
            else:
                raise RuntimeError("session is not the first or second argument in the function")
        else:
            raise RuntimeError("session not an args")
        func_return = await func(*args, **kwargs)
        return func_return

    @functools.wraps(func)
    async def wrapper_events(*args, **kwargs):
        func_mod_and_name = f"{func.__module__}.{func.__name__}"
        log.info(f"Starting {func_mod_and_name}")
        session_passed = False
        for arg in list(args) + list(kwargs.values()):
            if issubclass(type(arg), AsyncSession):
                session_passed = True
                break
        try:
            if session_passed is True:
                func_return = await func(*args, **kwargs)
            else:

                session: AsyncSession = _async_session_maker()
                try:
                    func_return = await _session_work(session, args, kwargs)
                except:  # noqa: E722
                    await session.rollback()
                    raise
                else:
                    await session.commit()
                finally:
                    await session.close()

            log.info(f"Finished {func_mod_and_name}")
            return func_return
        except Exception as e:
            log.exception(e)
            raise

    return wrapper_events
