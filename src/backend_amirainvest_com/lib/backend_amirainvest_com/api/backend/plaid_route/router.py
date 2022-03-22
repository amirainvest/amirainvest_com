from fastapi import APIRouter, Depends, Request, status
from fastapi.templating import Jinja2Templates

from backend_amirainvest_com.api.backend.plaid_route.controller import get_and_set_access_token, get_financial_accounts
from backend_amirainvest_com.api.backend.plaid_route.models import (
    FinancialAccount,
    LinkTokenResponse,
    PlaidTokenRequest,
    UpdatePlaidTokenRequest,
)
from backend_amirainvest_com.controllers.auth import auth_depends_user_id
from backend_amirainvest_com.controllers.plaid_controller import generate_link_token


router = APIRouter(prefix="/plaid", tags=["Plaid"])
templates = Jinja2Templates(directory="src/backend_amirainvest_com/lib/backend_amirainvest_com/api/backend/plaid_route")


@router.get("/", status_code=status.HTTP_200_OK)
async def get_plaid_route(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/accounts", status_code=status.HTTP_200_OK, response_model=list[FinancialAccount])
async def get_current_brokerage_accounts(token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    return await get_financial_accounts(user_id)


@router.post("/link", status_code=status.HTTP_200_OK, response_model=LinkTokenResponse)
async def get_link(update_request: UpdatePlaidTokenRequest, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    link_token = await generate_link_token(user_id, update_request.item_id, update_request.redirect_uri)
    return LinkTokenResponse(link_token=link_token)


@router.post("/token", status_code=status.HTTP_200_OK)
async def get_and_set_access_token_route(token_request: PlaidTokenRequest, token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    await get_and_set_access_token(
        user_id=user_id, public_token=token_request.public_token, is_update=token_request.is_update
    )
