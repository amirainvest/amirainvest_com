from brokerage_amirainvest_com.brokerages.brokerage_interface import TokenRepositoryInterface


class MockWithAccessToken(TokenRepositoryInterface):
    def __init__(self):
        pass

    def get_key(self, user_id: str) -> str:
        # Access token hard-coded from sandbox api
        return "access-sandbox-51d24c95-5ec4-4970-be74-0173419f246c"
