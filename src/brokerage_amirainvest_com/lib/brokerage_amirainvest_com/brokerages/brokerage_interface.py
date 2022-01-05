import abc
import uuid


class BrokerageInterface(abc.ABC):
    @abc.abstractmethod
    async def collect_investment_history(self, user_id: uuid.UUID):
        """
        Gets the history of a transaction...?
        """
        ...

    @abc.abstractmethod
    async def collect_current_holdings(self, user_id: uuid.UUID):
        """
        Gets a list of institutions
        """
        ...


class TokenRepositoryInterface(abc.ABC):
    @abc.abstractmethod
    def get_key(self, user_id: str) -> str:
        """
        Fetches the string associated with the account id
        """
        ...
