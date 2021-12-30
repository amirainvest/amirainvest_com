import datetime
import uuid
from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    sub: str
    name: str
    bio: str
    username: str
    picture_url: str
    email: str
    personal_site_url: str
    linkedin_profile: str
    email_verified: bool = False
    interests_value: bool
    interests_growth: bool
    interests_long_term: bool
    interests_short_term: bool
    interests_diversification_rating: int
    benchmark: str
    public_profile: bool
    public_performance: bool
    public_holdings: bool
    public_trades: bool
    is_claimed: bool
    is_deactivated: bool
    is_deleted: bool
    deleted_at: datetime.datetime
    created_at: datetime.datetime
    updated_at: datetime.datetime
    twitter_username: str
    youtube_channel_id: str
    substack_username: str


class UserUpdate(BaseModel):
    id: uuid.UUID
    sub: Optional[str]
    name: Optional[str]
    bio: Optional[str]
    username: Optional[str]
    picture_url: Optional[str]
    email: Optional[str]
    personal_site_url: Optional[str]
    linkedin_profile: Optional[str]
    email_verified: Optional[bool]
    interests_value: Optional[bool]
    interests_growth: Optional[bool]
    interests_long_term: Optional[bool]
    interests_short_term: Optional[bool]
    interests_diversification_rating: Optional[int]
    benchmark: Optional[str]
    public_profile: Optional[bool]
    public_performance: Optional[bool]
    public_holdings: Optional[bool]
    public_trades: Optional[bool]
    is_claimed: Optional[bool]
    is_deactivated: Optional[bool]
    is_deleted: Optional[bool]
    deleted_at: Optional[datetime.datetime]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
