from pydantic import BaseModel


class CreateModel(BaseModel):
    text: str
