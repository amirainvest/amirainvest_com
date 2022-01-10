from typing import cast, Union

from fastapi import APIRouter, Header

from backend_amirainvest_com.controllers import webhooks
from backend_amirainvest_com.controllers.auth import verify_webhook
from backend_amirainvest_com.models.webhooks import HoldingsUpdate, InvestmentsUpdate, TransactionsUpdate


router = APIRouter(prefix="/plaid", tags=["plaid"])


@router.post("/")
async def webhook_update(
    request: Union[TransactionsUpdate, HoldingsUpdate, InvestmentsUpdate], plaid_verification: str = Header(None)
):
    if verify_webhook(request, plaid_verification) is not True:
        return
    if request.webhook_type == "HOLDINGS":
        await webhooks.handle_holdings_change(cast(HoldingsUpdate, request))
        return
    if request.webhook_type == "INVESTMENTS_TRANSACTIONS":
        await webhooks.handle_investments_change(cast(InvestmentsUpdate, request))
        return
    if request.webhook_type == "TRANSACTIONS":
        print("Validating Transactions Webhook...")
