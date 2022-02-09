from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from backend_amirainvest_com.controllers.auth import auth_depends_user_id
from backend_amirainvest_com.controllers.plaid_controller import exchange_public_for_access_token, generate_link_token
from common_amirainvest_com.dynamo.models import BrokerageUser
from common_amirainvest_com.dynamo.utils import add_brokerage_user, get_brokerage_user, update_brokerage_user
from common_amirainvest_com.sqs.consts import BROKERAGE_DATA_QUEUE_URL
from common_amirainvest_com.sqs.models import Brokerage, BrokerageDataActions, BrokerageDataChange
from common_amirainvest_com.sqs.utils import add_message_to_queue
from backend_amirainvest_com.api.backend.plaid_route.models import PlaidTokenRequest


router = APIRouter(prefix="/plaid", tags=["Plaid"])
templates = Jinja2Templates(directory="src/backend_amirainvest_com/lib/backend_amirainvest_com/api/backend/plaid_route")


@router.get('/', status_code=status.HTTP_200_OK)
async def get_plaid(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})


@router.post("/link", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_link(token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    link_token = generate_link_token(user_id)
    return JSONResponse({"link_token": link_token})


# TODO Could move most of the logic to controller
@router.post("/token", status_code=status.HTTP_200_OK, response_class=JSONResponse)
async def get_token(token_request: PlaidTokenRequest, token=Depends(auth_depends_user_id)):
    public_token = token_request.public_token
    user_id = token["https://amirainvest.com/user_id"]
    exchange_response = exchange_public_for_access_token(public_token)
    access_token = exchange_response["access_token"]
    item_id = exchange_response["item_id"]
    brokerage_user = await get_brokerage_user(user_id)
    if brokerage_user is None:
        await add_brokerage_user(
            BrokerageUser(
                user_id=user_id,
                plaid_access_tokens={
                    item_id: access_token,
                },
            )
        )
    else:
        plaid_tokens = brokerage_user.plaid_access_tokens
        plaid_tokens[item_id] = access_token
        brokerage_user.plaid_access_tokens = plaid_tokens
        await update_brokerage_user(brokerage_user)

    add_message_to_queue(
        BROKERAGE_DATA_QUEUE_URL,
        BrokerageDataChange(
            brokerage=Brokerage.plaid,
            user_id=user_id,
            token_identifier=item_id,
            action=BrokerageDataActions.upsert_brokerage_account,
        ),
    )
