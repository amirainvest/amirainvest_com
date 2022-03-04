from pydantic import BaseModel


class BrokerageUser(BaseModel):
    user_id: str
    item_id: str
    access_token: str
