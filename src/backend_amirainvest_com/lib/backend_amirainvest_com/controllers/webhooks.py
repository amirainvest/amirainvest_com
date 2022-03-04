import arrow

from backend_amirainvest_com.models.webhooks import HoldingsUpdate, InvestmentsUpdate
from common_amirainvest_com.sqs.consts import BROKERAGE_DATA_QUEUE_URL
from common_amirainvest_com.sqs.models import Brokerage, BrokerageDataActions, BrokerageDataChange
from common_amirainvest_com.sqs.utils import add_message_to_queue

async def handle_holdings_change(holdings: HoldingsUpdate):
    add_message_to_queue(
        BROKERAGE_DATA_QUEUE_URL,
        BrokerageDataChange(
            brokerage=Brokerage.plaid,
            user_id=holdings.item_id,
            token_identifier=holdings.item_id,
            action=BrokerageDataActions.holdings_change,
            start_date=arrow.utcnow(),
            end_date=arrow.utcnow(),
        ),
    )


async def handle_investments_change(investments: InvestmentsUpdate):
    add_message_to_queue(
        BROKERAGE_DATA_QUEUE_URL,
        BrokerageDataChange(
            brokerage=Brokerage.plaid,
            user_id=investments.item_id,
            token_identifier=investments.item_id,
            action=BrokerageDataActions.investments_change,
            start_date=arrow.utcnow(),
            end_date=arrow.utcnow(),
        ),
    )
