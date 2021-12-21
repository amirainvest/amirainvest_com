from common_amirainvest_com.sqs.models import Brokerage, BrokerageDataActions, BrokerageDataChange
from common_amirainvest_com.sqs.sqs_utils import add_message_to_queue

from backend_amirainvest_com.config import BROKERAGE_DATA_QUEUE_URL
from backend_amirainvest_com.models.webhooks import HoldingsUpdate, InvestmentsUpdate


async def handle_holdings_change(holdings: HoldingsUpdate):
    add_message_to_queue(
        BROKERAGE_DATA_QUEUE_URL,
        BrokerageDataChange(
            brokerage=Brokerage.plaid, brokerage_user_id=holdings.item_id, action=BrokerageDataActions.holdings_change
        ),
    )


async def handle_investments_change(investments: InvestmentsUpdate):
    add_message_to_queue(
        BROKERAGE_DATA_QUEUE_URL,
        BrokerageDataChange(
            brokerage=Brokerage.plaid,
            brokerage_user_id=investments.item_id,
            action=BrokerageDataActions.investments_change,
        ),
    )
