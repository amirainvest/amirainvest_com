from backend_amirainvest_com.config import BROKERAGE_DATA_QUEUE_URL
import arrow

from backend_amirainvest_com.models.webhooks import HoldingsUpdate, InvestmentsUpdate
from common_amirainvest_com.sqs.models import Brokerage, BrokerageDataActions, BrokerageDataChange
# from common_amirainvest_com.sqs.utils import add_message_to_queue


async def handle_holdings_change(holdings: HoldingsUpdate):
    print(BrokerageDataChange(
        brokerage=Brokerage.plaid, brokerage_user_id=holdings.item_id, action=BrokerageDataActions.holdings_change,
        start_date=arrow.utcnow(), end_date=arrow.utcnow()
    ))
    # add_message_to_queue(
    #     BROKERAGE_DATA_QUEUE_URL,
    #     BrokerageDataChange(
    #         brokerage=Brokerage.plaid, brokerage_user_id=holdings.item_id, action=BrokerageDataActions.holdings_change
    #     ),
    # )


async def handle_investments_change(investments: InvestmentsUpdate):
    print("Hello!")
    # add_message_to_queue(
    #     BROKERAGE_DATA_QUEUE_URL,
    #     BrokerageDataChange(
    #         brokerage=Brokerage.plaid,
    #         brokerage_user_id=investments.item_id,
    #         action=BrokerageDataActions.investments_change,
    #     ),
    # )
