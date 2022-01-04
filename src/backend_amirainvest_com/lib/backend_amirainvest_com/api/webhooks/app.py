from fastapi import FastAPI
from starlette.responses import RedirectResponse

from backend_amirainvest_com.api.webhooks.routes import plaid_routes


app = FastAPI(title="Webhooks", version="0.1")

app.include_router(plaid_routes.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
