import asyncio


def run_async_function_synchronously(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(func(*args, **kwargs))
    loop.close()
    return results
