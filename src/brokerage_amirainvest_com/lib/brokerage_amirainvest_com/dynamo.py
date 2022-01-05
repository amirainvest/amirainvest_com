from typing import Optional

from brokerage_amirainvest_com.brokerages.interfaces import TokenRepositoryInterface
from common_amirainvest_com.dynamo.models import BrokerageUser
from common_amirainvest_com.dynamo.utils import get_brokerage_user


class TokenProvider(TokenRepositoryInterface):
    async def get_key(self, user_id: str) -> Optional[BrokerageUser]:
        response = await get_brokerage_user(user_id)
        return response
