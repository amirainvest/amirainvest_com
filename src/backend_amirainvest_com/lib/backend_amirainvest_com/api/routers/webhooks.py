from fastapi import APIRouter

from backend.controllers import webhooks
from backend.models.webhooks import HoldingsUpdate, InvestmentsUpdate


router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/plaid/holdings")
async def holdings_update(holdings: HoldingsUpdate):
    webhooks.handle_holdings_change(holdings)
    return


@router.post("/plaid/investments")
async def investments_update(investments: InvestmentsUpdate):
    webhooks.handle_investments_change(investments)
    return
