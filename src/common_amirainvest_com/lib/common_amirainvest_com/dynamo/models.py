from typing import Any

from pydantic import BaseModel


class BrokerageUser(BaseModel):
    # Partition Key
    user_id: str
    plaid_access_tokens: dict[str, Any]
