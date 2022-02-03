import pkg_resources
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
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
from backend_amirainvest_com.api.backend.portfolio.router import router as portfolio_router
from backend_amirainvest_com.api.routers import search, user_subscriptions
from backend_amirainvest_com.api.webhooks.app import app as webhooks_app
from common_amirainvest_com.utils.consts import ENVIRONMENT, Environments


app = FastAPI(title="Backend", version=pkg_resources.get_distribution("common_amirainvest_com").version)

app.include_router(admin_router)
app.include_router(user_router)
app.include_router(user_subscriptions.router)
app.include_router(post_router)
app.include_router(bookmark_router)
app.include_router(hust_request_router)
app.include_router(broadcast_router)
app.include_router(code_challenge_router)
app.include_router(search.router)
app.include_router(plaid_router)
app.include_router(application_router)
app.include_router(user_feedback_router)
app.include_router(portfolio_router)

app.mount("/webhooks", webhooks_app)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


if ENVIRONMENT != Environments.local.value:
    app = SentryAsgiMiddleware(app)  # type: ignore
