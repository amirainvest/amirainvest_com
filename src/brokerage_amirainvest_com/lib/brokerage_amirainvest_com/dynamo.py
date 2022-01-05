from brokerage_amirainvest_com.brokerages.interfaces import TokenRepositoryInterface
from common_amirainvest_com.dynamo.models import BrokerageUser  # type: ignore


class TokenProvider(TokenRepositoryInterface):
    def __init__(self):
        pass

    def get_key(self, user_id: str) -> BrokerageUser:
        pass
