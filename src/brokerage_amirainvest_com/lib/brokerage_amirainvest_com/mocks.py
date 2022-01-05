from brokerage_amirainvest_com.brokerages.brokerage_interface import TokenRepositoryInterface


class MockWithAccessToken(TokenRepositoryInterface):
    def __init__(self):
        pass

    def get_key(self, user_id: str) -> str:
        # Access token hard-coded from sandbox api
        return "access-sandbox-1001d961-0408-480f-822a-f836a62332ac"
