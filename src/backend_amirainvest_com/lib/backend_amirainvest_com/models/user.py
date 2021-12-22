import datetime

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
