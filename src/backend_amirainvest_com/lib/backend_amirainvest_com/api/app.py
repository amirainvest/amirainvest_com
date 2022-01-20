import subprocess

from fastapi import FastAPI

# from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.responses import RedirectResponse

from backend_amirainvest_com.api.backend.admin.router import router as admin_router
from backend_amirainvest_com.api.backend.application.router import router as application_router
from backend_amirainvest_com.api.backend.bookmark.router import router as bookmark_router
from backend_amirainvest_com.api.backend.broadcast_request.router import router as broadcast_router
from backend_amirainvest_com.api.backend.code_challenge.router import router as code_challenge_router
from backend_amirainvest_com.api.backend.husk_request.router import router as hust_request_router
from backend_amirainvest_com.api.backend.plaid_route.router import router as plaid_router
from backend_amirainvest_com.api.backend.post_route.router import router as post_router
from backend_amirainvest_com.api.backend.user_feedback.router import router as user_feedback_router
from backend_amirainvest_com.api.backend.user_route.router import router as user_router
from backend_amirainvest_com.api.routers import feed, search, user_subscriptions
from backend_amirainvest_com.api.webhooks.app import app as webhooks_app


app = FastAPI(title="Backend", version="0.1")

app.include_router(admin_router)
app.include_router(user_router)
app.include_router(user_subscriptions.router)
app.include_router(feed.router)
app.include_router(post_router)
app.include_router(bookmark_router)
app.include_router(hust_request_router)
app.include_router(broadcast_router)
app.include_router(code_challenge_router)
app.include_router(search.router)
app.include_router(plaid_router)
app.include_router(application_router)
app.include_router(user_feedback_router)

app.mount("/webhooks", webhooks_app)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


# app = SentryAsgiMiddleware(app)


def run():
    subprocess.run("uvicorn backend_amirainvest_com.api.app:app --reload --host 0.0.0.0 --port 5000".split(" "))


if __name__ == "__main__":
    run()
