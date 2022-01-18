import uuid
from typing import List, Optional

from pydantic import BaseModel


class UserUpdate(BaseModel):
    name: Optional[str]
    bio: Optional[str]
    personal_site_url: Optional[str]
    linkedin_profile: Optional[str]
    interests_value: Optional[bool]
    interests_growth: Optional[bool]
    interests_long_term: Optional[bool]
    interests_short_term: Optional[bool]
    interests_diversification_rating: Optional[int]
    benchmark: Optional[str]
    chip_labels: Optional[List[str]]
    public_profile: Optional[bool]
    public_performance: Optional[bool]
    public_holdings: Optional[bool]
    public_trades: Optional[bool]
    is_deactivated: Optional[bool]
    is_deleted: Optional[bool]


class InitReturnModel(BaseModel):
    id: uuid.UUID


class InitPostModel(BaseModel):
    name: str
    username: str
    email: str
