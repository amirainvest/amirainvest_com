from typing import Optional

from brokerage_amirainvest_com.brokerages.interfaces import TokenRepositoryInterface
from common_amirainvest_com.dynamo.models import BrokerageUser
from common_amirainvest_com.dynamo.utils import get_brokerage_user_item


class TokenProvider(TokenRepositoryInterface):
    async def get_key(self, user_id: str, item_id: str) -> Optional[BrokerageUser]:
        response = await get_brokerage_user_item(user_id=user_id, item_id=item_id)
        return response
