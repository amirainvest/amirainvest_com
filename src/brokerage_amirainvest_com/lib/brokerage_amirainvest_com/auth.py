import subprocess

from common_amirainvest_com.utils.consts import PLAID_SECRET, PLAID_CLIENT_ID
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
import time
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, Form, Cookie
import boto3
from pydantic import BaseModel
from mypy_boto3_dynamodb import DynamoDBServiceResource, DynamoDBClient
from typing import Optional
from common_amirainvest_com.schemas.schema import FinancialAccounts, Users
from common_amirainvest_com.utils.decorators import Session
from sqlalchemy.ext.asyncio import AsyncSession
from backend_amirainvest_com.controllers.users import create_user
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from sqlalchemy import select


# Table: brokerage_users
class BrokerageUser(BaseModel):
    amira_user_id: str  # Partition Key
    plaid_access_tokens: dict[str, str]


dynamo_resource: DynamoDBServiceResource = boto3.resource('dynamodb', endpoint_url="http://dynamo:8000")
dynamo_client: DynamoDBClient = boto3.client('dynamodb', endpoint_url='http://dynamo:8000')


@Session
async def get_financial_account(session: AsyncSession, item_id: str) -> FinancialAccounts:
    financial_account = await session.execute(FinancialAccounts).where(FinancialAccounts.plaid_id == item_id)
    return financial_account.scalars().all()


@Session
async def add_financial_account(session: AsyncSession, financial_account: FinancialAccounts):
    session.add(financial_account)
    return financial_account


async def create_dynamo_brokerage_users():
    try:
        table = dynamo_resource.create_table(
            TableName='brokerage_users',
            KeySchema=[
                {
                    'AttributeName': 'amira_user_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'amira_user_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        table_status = table.table_status
        while table_status != 'ACTIVE':
            brokerage_user = dynamo_resource.Table('brokerage_user')
            table_status = brokerage_user.table_status
    except dynamo_client.exceptions.ResourceInUseException:
        pass
    except Exception as e:
        print(e)


async def add_brokerage_user(brokerage_user: BrokerageUser):
    try:
        item = {
            'amira_user_id': brokerage_user.amira_user_id,
            'plaid_access_tokens': brokerage_user.plaid_access_tokens
        }
        table = dynamo_resource.Table('brokerage_users')
        res = table.put_item(Item=item)
        print(res)
    except Exception as e:
        print(e)
        pass


async def get_brokerage_user(amira_user_id: str) -> Optional[BrokerageUser]:
    try:
        table = dynamo_resource.Table('brokerage_users')
        brokerage_user = table.get_item(Key={'user_id': amira_user_id})
        return BrokerageUser(**brokerage_user)
    except Exception as e:
        return None


async def update_brokerage_user(brokerage_user: BrokerageUser):
    try:
        table = dynamo_resource.Table('brokerage_users')
        table.update_item(
            Key={'user_id': brokerage_user.amira_user_id},
            ReturnValues='NONE',
            UpdateExpression="set plaid_access_tokens=:p",
            ExpressionAttributeValues={
                ':p': brokerage_user.plaid_access_tokens
            }
        )
    except Exception as e:
        pass


@Session
async def get_amira_user(session: AsyncSession) -> Users:
    user = await session.execute(select(Users).limit(1))
    return user.scalar()


app = FastAPI()

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
PRODUCTS = ['investments', 'auth']
PLAID_COUNTRY_CODES = "US,"

templates = Jinja2Templates(directory="src/brokerage_amirainvest_com/lib/brokerage_amirainvest_com/templates")


@app.get("/link", response_class=HTMLResponse)
async def link_get(request: Request):
    request = LinkTokenCreateRequest(
        products=[Products("investments"), Products("transactions")],
        client_name='Plaid Test',
        country_codes=[CountryCode('US')],
        language='en',
        user=LinkTokenCreateRequestUser(
            client_user_id=str(time.time())
        ),
    )

    response = client.link_token_create(request)
    link_token = response['link_token']
    res = templates.TemplateResponse("link.html", {"request": request, 'link_token': link_token})
    user = await get_amira_user()
    res.set_cookie(key='amira_user_id', value=str(user.id))
    return res


# TODO: DB Updates...
@app.post("/link")
async def link_post(public_token: str = Form(...), amira_user_id: Optional[str] = Cookie(None)):
    try:
        # do something where we decode the JWT of the user via auth
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )

        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']

        # Check to see if record for user exists first, if exists update, otherwise insert
        brokerage_user = await get_brokerage_user(amira_user_id)
        print("BROKERAGE USER: ", brokerage_user)
        if brokerage_user is None:
            print("Adding brokerage user...")
            await add_brokerage_user(
                BrokerageUser(
                    amira_user_id=amira_user_id,
                    plaid_access_tokens={
                        item_id: access_token,
                    }
                )
            )
            # await add_financial_account(
            #     financial_account=FinancialAccounts(
            #         user_id=amira_user_id,
            #         plaid_item_id=item_id,
            #         plaid_id="",
            #         official_account_name="",
            #         user_assigned_account_name="",
            #     )
            # )
            return

        # brokerage_user.plaid_access_tokens[item_id] = access_token
        # update_brokerage_user(brokerage_user)
    except plaid.ApiException as e:
        print(e.body)


def run():
    subprocess.run("uvicorn brokerage_amirainvest_com.auth:app --reload --host 0.0.0.0 --port 5000".split(" "))


async def add_user():
    user = await get_amira_user()
    if user is not None:
        return

    await create_user(
        {
            "sub": "1234",
            "name": "Test User",
            "username": "test123",
            "picture_url": "http://google.com",
            "email": "test@test.com"
        }
    )


async def test():
    try:
        await create_dynamo_brokerage_users()
        res = await add_brokerage_user(
            brokerage_user=BrokerageUser(
                amira_user_id="amira-user-id-123",
                plaid_access_tokens={
                    "p": "1"
                }
            )
        )
        print(res)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    # run_async_function_synchronously(test)
    run()
