import uvicorn  # type: ignore
from uvicorn.workers import UvicornWorker  # type: ignore


class ProductionUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "host": "0.0.0.0",
        "port": "5000",
        "loop": "asyncio",
        "http": "h11",
        "lifespan": "off",
        "ws": "none",
        "interface": "asgi3",
        "proxy_headers": "true",
        "limit_concurrency": 10,
        "backlog": 2048,
    }


def local_run():
    uvicorn.run("backend_amirainvest_com.main:app", port=5000, host="0.0.0.0", reload=True)


if __name__ == "__main__":
    local_run()
