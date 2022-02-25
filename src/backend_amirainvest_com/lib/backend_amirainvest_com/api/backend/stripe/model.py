from pydantic import BaseModel

class StripeModel(BaseModel):
    stripe_id: str

