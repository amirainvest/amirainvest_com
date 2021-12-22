from brokerage_amirainvest_com.brokerages.brokerage_interface import TokenRepositoryInterface
from brokerage_amirainvest_com.models import Institution


class RobinhoodBrokerage:
    def get_institutions(self, offset: int) -> list[Institution]:
        pass

    token_repository: TokenRepositoryInterface
    client: None

    def __init__(self, token_repository: TokenRepositoryInterface):
        self.token_repository = token_repository

    def get_investment_history(self, user_id: str, offset: int = 0):
        pass
