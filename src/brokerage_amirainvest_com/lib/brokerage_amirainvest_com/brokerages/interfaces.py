import abc
import uuid

from common_amirainvest_com.dynamo.models import BrokerageUser  # type: ignore


class BrokerageInterface(abc.ABC):
    @abc.abstractmethod
    async def collect_investment_history(self, user_id: uuid.UUID, item_id: str):
        """
        Gets the history of a transaction...?
        """
        ...

    @abc.abstractmethod
    async def collect_current_holdings(self, user_id: uuid.UUID, item_id: str):
        """
        Gets a list of institutions
        """
        ...


class TokenRepositoryInterface(abc.ABC):
    @abc.abstractmethod
    def get_key(self, user_id: str) -> BrokerageUser:
        """
        Fetches the string associated with the account id
        """
        ...
