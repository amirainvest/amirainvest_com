import datetime
from typing import Optional

from pydantic import BaseModel

from common_amirainvest_com.schemas.schema import UserFeedbackModel as GetModel


assert GetModel


class CreateModel(BaseModel):
    text: str
    created_at: Optional[datetime.datetime]
