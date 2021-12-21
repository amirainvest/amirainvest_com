import subprocess

from fastapi import FastAPI
from starlette.responses import RedirectResponse

from backend_amirainvest_com.api.routers import (
    admin,
    bookmarks,
    broadcast_requests,
    feed,
    husk_requests,
    posts,
    user_subscriptions,
    users,
)


app = FastAPI(title="Backend", version="0.1")
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(user_subscriptions.router)
app.include_router(feed.router)
app.include_router(posts.router)
app.include_router(bookmarks.router)
app.include_router(husk_requests.router)
app.include_router(broadcast_requests.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


def run():
    subprocess.run("uvicorn backend_amirainvest_com.api.app:app --reload --host 0.0.0.0 --port 5000".split(" "))

s
if __name__ == "__main__":
    run()
