from common_amirainvest_com.dynamo.models import BrokerageUser
from common_amirainvest_com.dynamo.utils import add_brokerage_user
from common_amirainvest_com.sqs.consts import BROKERAGE_DATA_QUEUE_URL
from common_amirainvest_com.sqs.models import Brokerage, BrokerageDataActions, BrokerageDataChange
from common_amirainvest_com.sqs.utils import add_message_to_queue
from backend_amirainvest_com.controllers.plaid_controller import exchange_public_for_access_token
from backend_amirainvest_com.api.backend.plaid_route.models import BadItem
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from common_amirainvest_com.schemas.schema import BadPlaidItems
from common_amirainvest_com.utils.decorators import Session

from typing import Optional

from sqlalchemy import delete


async def get_and_set_access_token(user_id: str, public_token: str, is_update: bool):
    exchange_response = exchange_public_for_access_token(public_token)
    access_token = exchange_response["access_token"]
    item_id = exchange_response["item_id"]
    await add_brokerage_user(BrokerageUser(item_id=item_id, access_token=access_token, user_id=user_id))

    if is_update:
        await remove_bad_item(user_id=user_id, item_id=item_id)
        return

    add_message_to_queue(
        BROKERAGE_DATA_QUEUE_URL,
        BrokerageDataChange(
            brokerage=Brokerage.plaid,
            user_id=user_id,
            token_identifier=item_id,
            action=BrokerageDataActions.upsert_brokerage_account,
        ),
    )


@Session
async def get_bad_items(session: AsyncSession, user_id: str) -> Optional[list[BadItem]]:
    response = await session.execute(select(BadPlaidItems).where(BadPlaidItems.user_id == user_id))
    items = response.scalars().all()
    if items is None:
        return None

    return [BadItem.parse_obj(item.dict()) for item in items]


@Session
async def remove_bad_item(session: AsyncSession, user_id: str, item_id: str):
    await session.execute(
        delete(BadPlaidItems).where(BadPlaidItems.user_id == user_id, BadPlaidItems.plaid_item_id == item_id)
    )
