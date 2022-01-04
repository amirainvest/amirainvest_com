from fastapi import APIRouter, Header

from backend_amirainvest_com.controllers import webhooks
from backend_amirainvest_com.controllers.auth import verify_webhook
from backend_amirainvest_com.models.webhooks import HoldingsUpdate, InvestmentsUpdate, TransactionsUpdate


router = APIRouter(prefix="/plaid", tags=["plaid"])


# Used for Sandbox Testing -- Plaid only exposes transactions
@router.post("/transactions")
async def transactions_update(transactions: TransactionsUpdate, plaid_verification: str = Header(None)):
    if verify_webhook(transactions, plaid_verification) is not True:
        return


@router.post("/holdings")
async def holdings_update(holdings: HoldingsUpdate, plaid_verification: str = Header(None)):
    if verify_webhook(holdings, plaid_verification) is not True:
        return
    await webhooks.handle_holdings_change(holdings)


@router.post("/investments")
async def investments_update(investments: InvestmentsUpdate, plaid_verification: str = Header(None)):
    if verify_webhook(investments, plaid_verification) is not True:
        return
    await webhooks.handle_investments_change(investments)
