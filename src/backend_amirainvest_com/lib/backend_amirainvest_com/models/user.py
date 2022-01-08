import datetime

from pydantic import BaseModel
from typing import Optional, List


class UserCreate(BaseModel):
    sub: str
    name: str
    bio: Optional[str]
    username: str
    picture_url: str
    email: str
    personal_site_url: Optional[str]
    linkedin_profile: Optional[str]
    email_verified: bool
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
    is_claimed: Optional[bool]
