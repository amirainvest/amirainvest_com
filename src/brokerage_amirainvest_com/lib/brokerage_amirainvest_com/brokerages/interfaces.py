import abc
from typing import Optional

from common_amirainvest_com.dynamo.models import BrokerageUser


class BrokerageInterface(abc.ABC):
    @abc.abstractmethod
    async def collect_investment_history(self, user_id: str, item_id: str):
        """
        Gets the history of a transaction...?
        """
        ...

    @abc.abstractmethod
    async def collect_current_holdings(self, user_id: str, item_id: str):
        """
        Gets a list of institutions
        """
        ...

    @abc.abstractmethod
    async def compute_holdings_history(self, user_id: str, item_id: str):
        """
        Compute the holdings history
        """


class TokenRepositoryInterface(abc.ABC):
    @abc.abstractmethod
    async def get_key(self, user_id: str, item_id: str) -> Optional[BrokerageUser]:
        """
        Fetches the string associated with the account id
        """
        ...
