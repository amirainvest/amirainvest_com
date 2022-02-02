import datetime
import enum
import uuid
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    Column,
    DECIMAL,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime


Base = declarative_base()


class UTCNow(expression.FunctionElement):  # type: ignore[name-defined]
    type = DateTime()


@compiles(UTCNow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class ToDict:
    # This is just to shut up Pycharm
    def __init__(self, *args, **kwargs):
        pass

    def dict(self) -> dict:
        return_dict = {}
        key: str
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                return_dict[key] = value
        return return_dict


class Users(Base, ToDict):
    __tablename__ = "users"
    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    sub = Column(String, nullable=False)
    name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

    picture_url = Column(String)
    bio = Column(String)
    personal_site_url = Column(String)
    linkedin_profile = Column(String)
    email_verified = Column(Boolean, default=False)
    interests_diversification_rating = Column(Integer)
    benchmark = Column(String)
    trading_strategies = Column(ARRAY(String))
    chip_labels = Column(ARRAY(String))
    public_profile = Column(Boolean)
    public_performance = Column(Boolean)
    public_holdings = Column(Boolean)
    public_trades = Column(Boolean)
    is_claimed = Column(Boolean)
    is_deactivated = Column(Boolean)
    is_deleted = Column(Boolean)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class UsersModel(BaseModel):
    id: uuid.UUID
    sub: str
    name: str
    username: str
    email: str

    picture_url: Optional[str]
    bio: Optional[str]
    personal_site_url: Optional[str]
    linkedin_profile: Optional[str]
    email_verified: bool
    interests_diversification_rating: Optional[int]
    benchmark: Optional[str]
    trading_strategies: Optional[List[str]]
    chip_labels: Optional[List[str]]
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


class Watchlists(Base, ToDict):
    __tablename__ = "watchlists"
    id = Column(Integer, primary_key=True, unique=True)
    creator_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    tickers = Column(ARRAY(String), nullable=False)
    note = Column(String)
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class WatchlistsModel(BaseModel):
    id: int
    creator_id: uuid.UUID
    name: str
    tickers: List[str]
    note: Optional[str]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class WatchlistFollows(Base, ToDict):
    __tablename__ = "watchlist_follows"
    id = Column(Integer, primary_key=True, unique=True)
    follower_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class WatchlistFollowsModel(BaseModel):
    id: int
    follower_id: uuid.UUID
    watchlist_id: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class Benchmarks(Base):
    __tablename__ = "benchmarks"
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)


class TradingStrategies(Base):
    __tablename__ = "trading_strategies"
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)


class ChipLabels(Base):
    __tablename__ = "chip_labels"
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)


class BroadcastRequests(Base, ToDict):
    __tablename__ = "broadcast_requests"
    id = Column(Integer, primary_key=True, unique=True)
    subscriber_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creator_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())

    subscriber: Users = relationship(
        "Users", backref="broadcast_requester", passive_deletes=True, cascade="all,delete", foreign_keys=[subscriber_id]
    )
    creator: Users = relationship(
        "Users", backref="creator_requested", passive_deletes=True, cascade="all,delete", foreign_keys=[creator_id]
    )


class BroadcastRequestsModel(BaseModel):
    id: int
    subscriber_id: uuid.UUID
    creator_id: uuid.UUID
    created_at: Optional[datetime.datetime]


class SubscriptionLevel(enum.Enum):
    standard = "standard"
    premium = "premium"


class UserSubscriptions(Base, ToDict):
    __tablename__ = "user_subscriptions"
    id = Column(Integer, primary_key=True, unique=True)
    subscriber_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creator_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_level = Column(Enum(SubscriptionLevel), default=SubscriptionLevel.standard.value, nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
    is_deleted = Column(Boolean, nullable=False)

    subscriber: Users = relationship(
        "Users", backref="subscriber", passive_deletes=True, cascade="all,delete", foreign_keys=[subscriber_id]
    )
    creator: Users = relationship(
        "Users", backref="creator", passive_deletes=True, cascade="all,delete", foreign_keys=[creator_id]
    )


class UserSubscriptionsModel(BaseModel):
    id: int
    subscriber_id: uuid.UUID
    creator_id: uuid.UUID
    subscription_level: SubscriptionLevel
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    is_deleted: bool


class UserMediaErrors(Base, ToDict):
    __tablename__ = "user_media_errors"
    id = Column(Integer, primary_key=True, unique=True)
    user_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String, nullable=False)
    error_at = Column(String, nullable=False)
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)

    creator: Users = relationship("Users", backref="user_media_errors", passive_deletes=True, cascade="all,delete")


class UserFeedback(Base, ToDict):
    __tablename__ = "user_feedback"
    id = Column(Integer, primary_key=True, unique=True)
    user_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)

    user: Users = relationship("Users", backref="user_feedback", passive_deletes=True, cascade="all,delete")


class UserFeedbackModel(BaseModel):
    id: int
    user_id: uuid.UUID
    text: str
    created_at: Optional[datetime.datetime]


class SubstackUsers(Base, ToDict):
    __tablename__ = "substack_users"
    username = Column(String, primary_key=True, unique=True)
    user_url = Column(String)
    creator_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_deleted = Column(Boolean)
    created_at = Column(DateTime, server_default=UTCNow())

    creator: Users = relationship("Users", backref="substack_users", passive_deletes=True, cascade="all,delete")


class SubstackArticles(Base, ToDict):
    __tablename__ = "substack_articles"
    article_id = Column(String, primary_key=True, unique=True, nullable=False)
    url = Column(String)
    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    author = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())
    username = Column(String, ForeignKey("substack_users.username", ondelete="CASCADE"), nullable=False)

    substack_user: SubstackUsers = relationship(
        "SubstackUsers", backref="substack_articles", passive_deletes=True, cascade="all,delete"
    )


class YouTubers(Base, ToDict):
    __tablename__ = "youtubers"
    channel_id = Column(String, primary_key=True, unique=True)
    creator_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String)
    channel_username = Column(String)
    profile_img_url = Column(String)
    description = Column(String)
    subscriber_count = Column(Integer)
    video_count = Column(Integer)
    is_deleted = Column(Boolean)
    created_at = Column(DateTime, server_default=UTCNow())

    creator: Users = relationship("Users", backref="youtubers", passive_deletes=True, cascade="all,delete")


class YouTubeVideos(Base, ToDict):
    __tablename__ = "youtube_videos"
    video_id = Column(String, primary_key=True, unique=True)
    title = Column(String)
    published_at = Column(DateTime, nullable=False)
    video_url = Column(String)
    embed_url = Column(String)
    playlist_id = Column(String)
    channel_id = Column(String, ForeignKey("youtubers.channel_id", ondelete="CASCADE"))
    created_at = Column(DateTime, server_default=UTCNow())
    youtuber: YouTubers = relationship(
        "YouTubers", backref="youtube_video_creator", passive_deletes=True, cascade="all,delete"
    )


class TwitterUsers(Base, ToDict):
    __tablename__ = "twitter_users"
    twitter_user_id = Column(String, primary_key=True, unique=True)
    creator_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String)
    username = Column(String, nullable=False)
    profile_img_url = Column(String)
    profile_url = Column(String)
    follower_count = Column(Integer)
    following_count = Column(Integer)
    tweet_count = Column(Integer)
    is_deleted = Column(Boolean)
    created_at = Column(DateTime, server_default=UTCNow())

    creator: Users = relationship("Users", backref="twitter_users", passive_deletes=True, cascade="all,delete")


class Tweets(Base, ToDict):
    __tablename__ = "tweets"
    tweet_id = Column(String, primary_key=True, unique=True)
    twitter_user_id = Column(String, ForeignKey("twitter_users.twitter_user_id", ondelete="CASCADE"))
    language = Column(String)
    text = Column(String)
    possibly_sensitive = Column(Boolean)
    created_at = Column(DateTime, server_default=UTCNow())
    retweet_count = Column(Integer)
    reply_count = Column(Integer)
    like_count = Column(Integer)
    quote_count = Column(Integer)
    tweet_url = Column(String)
    embed = Column(String)

    twitter_user: TwitterUsers = relationship(
        "TwitterUsers", backref="tweets", passive_deletes=True, cascade="all,delete"
    )


class TweetAnnotations(Base, ToDict):
    __tablename__ = "tweet_annotations"
    id = Column(Integer, primary_key=True, unique=True)
    tweet_id = Column(String, ForeignKey("tweets.tweet_id", ondelete="CASCADE"), unique=True)
    start = Column(Integer)
    end = Column(Integer)
    probability = Column(Integer)
    annotation_type = Column(String)
    normalized_text = Column(String)

    tweet: Tweets = relationship("Tweets", backref="tweet_annotations", passive_deletes=True, cascade="all,delete")


class TweetCashtags(Base, ToDict):
    __tablename__ = "tweet_cashtags"
    id = Column(Integer, primary_key=True, unique=True)
    tweet_id = Column(String, ForeignKey("tweets.tweet_id", ondelete="CASCADE"), unique=True)
    start = Column(Integer)
    end = Column(Integer)
    tag = Column(String)

    tweet: Tweets = relationship("Tweets", backref="tweet_cashtags", passive_deletes=True, cascade="all,delete")


class TweetHashtags(Base, ToDict):
    __tablename__ = "tweet_hashtags"
    id = Column(Integer, primary_key=True, unique=True)
    tweet_id = Column(String, ForeignKey("tweets.tweet_id", ondelete="CASCADE"), unique=True)
    start = Column(Integer)
    end = Column(Integer)
    tag = Column(String)

    tweet: Tweets = relationship("Tweets", backref="tweet_hashtags", passive_deletes=True, cascade="all,delete")


class TweetMentions(Base, ToDict):
    __tablename__ = "tweet_mentions"
    id = Column(Integer, primary_key=True, unique=True)
    tweet_id = Column(String, ForeignKey("tweets.tweet_id", ondelete="CASCADE"), unique=True)
    start = Column(Integer)
    end = Column(Integer)
    username = Column(String)

    tweet: Tweets = relationship("Tweets", backref="tweet_mentions", passive_deletes=True, cascade="all,delete")


class TweetURLs(Base, ToDict):
    __tablename__ = "tweet_urls"
    id = Column(Integer, primary_key=True, unique=True)
    tweet_id = Column(String, ForeignKey("tweets.tweet_id", ondelete="CASCADE"), unique=True)
    start = Column(Integer)
    end = Column(Integer)
    url = Column(String)
    expanded_url = Column(String)
    display_url = Column(String)
    status = Column(Integer)
    title = Column(String)
    unwound_url = Column(String)
    images = Column(String)
    description = Column(String)

    tweet: Tweets = relationship("Tweets", backref="tweet_urls", passive_deletes=True, cascade="all,delete")


class Posts(Base, ToDict):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, unique=True)
    creator_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    platform = Column(String)
    platform_user_id = Column(String)
    platform_post_id = Column(String)
    profile_img_url = Column(String)
    text = Column(String)
    html = Column(String)
    title = Column(String)
    profile_url = Column(String)
    photos = Column(ARRAY(String))
    chip_labels = Column(ARRAY(String))
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)

    # TODO I think some of these relationships are not defined correctly.
    creator: Users = relationship(
        "Users", backref="post_creator", passive_deletes=True, cascade="all,delete", foreign_keys=[creator_id]
    )


class PostsModel(BaseModel):
    id: int
    creator_id: uuid.UUID
    platform: str
    platform_user_id: Optional[str]
    platform_post_id: Optional[str]
    profile_img_url: Optional[str]
    text: Optional[str]
    html: Optional[str]
    title: Optional[str]
    profile_url: Optional[str]
    photos: Optional[List[str]]
    chip_labels: Optional[List[str]]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class PostLikes(Base, ToDict):
    __tablename__ = "post_likes"
    user_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    liked_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)

    post: Posts = relationship(
        "Posts", backref="liked_post", passive_deletes=True, cascade="all,delete", foreign_keys=[post_id]
    )
    user: Users = relationship(
        "Users", backref="post_liker", passive_deletes=True, cascade="all,delete", foreign_keys=[user_id]
    )


class PostComments(Base, ToDict):
    __tablename__ = "post_comments"
    id = Column(Integer, primary_key=True, unique=True)
    user_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)

    post: Posts = relationship(
        "Posts", backref="commented_post", passive_deletes=True, cascade="all,delete", foreign_keys=[post_id]
    )
    user: Users = relationship(
        "Users", backref="post_commenter", passive_deletes=True, cascade="all,delete", foreign_keys=[user_id]
    )


class PostReads(Base, ToDict):
    __tablename__ = "post_reads"
    id = Column(Integer, primary_key=True, unique=True)
    user_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    read_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
    time_read_seconds = Column(Float, nullable=False)

    post: Posts = relationship(
        "Posts", backref="read_post", passive_deletes=True, cascade="all,delete", foreign_keys=[post_id]
    )
    user: Users = relationship(
        "Users", backref="post_reader", passive_deletes=True, cascade="all,delete", foreign_keys=[user_id]
    )


class Bookmarks(Base, ToDict):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, unique=True)
    user_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
    is_deleted = Column(Boolean, nullable=False)

    user: Users = relationship(
        "Users", backref="bookmarker", passive_deletes=True, cascade="all,delete", foreign_keys=[user_id]
    )
    post: Posts = relationship(
        "Posts", backref="bookmarked_post", passive_deletes=True, cascade="all,delete", foreign_keys=[post_id]
    )


class BookmarkModel(BaseModel):
    id: int
    user_id: uuid.UUID
    post_id: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    is_deleted: bool


class HuskPlatforms(enum.Enum):
    youtube = "YouTube"
    substack = "Substack"
    twitter = "Twitter"


class HuskRequests(Base, ToDict):
    __tablename__ = "husk_requests"
    id = Column(Integer, primary_key=True, unique=True)
    provided_name = Column(String, nullable=False)
    platform_id = Column(String, nullable=False)
    platform = Column(Enum(HuskPlatforms), nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())
    fulfilled = Column(Boolean)


class HuskRequestsModel(BaseModel):
    id: int
    provided_name: str
    platform: HuskPlatforms
    platform_id: str
    created_at: Optional[datetime.datetime]
    fulfilled: Optional[bool]


class FinancialInstitutions(Base, ToDict):
    __tablename__ = "financial_institutions"
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    plaid_id = Column(String, unique=True)
    third_party_institution_id = Column(String, unique=True)
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
    created_at = Column(DateTime, server_default=UTCNow())


class FinancialAccounts(Base, ToDict):
    __tablename__ = "financial_accounts"
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    user_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plaid_item_id = Column(String)
    plaid_id = Column(String, unique=True)
    official_account_name = Column(String)
    user_assigned_account_name = Column(String)
    available_to_withdraw = Column(DECIMAL(19, 4))
    current_funds = Column(DECIMAL(19, 4))
    mask = Column(String)
    type = Column(String)
    sub_type = Column(String)
    limit = Column(DECIMAL(19, 4))
    iso_currency_code = Column(String)
    unofficial_currency_code = Column(String)
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
    created_at = Column(DateTime, server_default=UTCNow())


class FinancialAccountTransactions(Base, ToDict):
    __tablename__ = "financial_account_transactions"
    id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    account_id = Column(Integer, ForeignKey("financial_accounts.id"), nullable=False)
    security_id = Column(Integer, ForeignKey("securities.id"))
    type = Column(String, nullable=False)
    subtype = Column(String, nullable=False)
    plaid_investment_transaction_id = Column(String, unique=True, nullable=False)
    posting_date = Column(DateTime, nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(DECIMAL, nullable=False)
    value_amount = Column(DECIMAL(19, 4), nullable=False)
    price = Column(DECIMAL(19, 4), nullable=False)
    fees = Column(DECIMAL(19, 4))
    created_at = Column(DateTime, server_default=UTCNow())
    iso_currency_code = Column(String)
    unofficial_currency_code = Column(String)


class FinancialAccountCurrentHoldings(Base, ToDict):
    __tablename__ = "financial_account_current_holdings"
    __table_args__ = (UniqueConstraint("account_id", "security_id"),)
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False)
    user_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("financial_accounts.id"), nullable=False)
    security_id = Column(Integer, ForeignKey("securities.id"), nullable=False)
    latest_price = Column(DECIMAL(19, 4), nullable=False)
    latest_price_date = Column(DateTime)
    institution_value = Column(DECIMAL(19, 4), nullable=False)
    cost_basis = Column(DECIMAL(19, 4))
    quantity = Column(DECIMAL(19, 4), nullable=False)
    iso_currency_code = Column(String)
    unofficial_currency_code = Column(String)
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
    created_at = Column(DateTime, server_default=UTCNow())


class PlaidSecurities(Base, ToDict):
    __tablename__ = "plaid_securities"
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    plaid_security_id = Column(String, unique=True)
    name = Column(String, nullable=False)
    ticker_symbol = Column(String, unique=True)
    isin = Column(String)
    cusip = Column(String)
    sedol = Column(String)
    institution_id = Column(Integer, ForeignKey("financial_institutions.id"))
    plaid_institution_security_id = Column(String)
    is_cash_equivalent = Column(Boolean)
    type = Column(String)
    iso_currency_code = Column(String)
    unofficial_currency_code = Column(String)
    plaid_update_type = Column(String)
    plaid_webhook_url = Column(String)
    last_updated = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
    created_at = Column(DateTime, server_default=UTCNow())


class PlaidSecurityPrices(Base, ToDict):
    __tablename__ = "plaid_security_prices"
    __table_args__ = (UniqueConstraint("price_time", "plaid_securities_id"),)
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False)
    plaid_securities_id = Column(Integer, ForeignKey("plaid_securities.id"), nullable=False)
    price = Column(DECIMAL(19, 4), nullable=False)
    price_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())


class BrokerageJobsStatus(enum.Enum):
    pending = "PENDING"
    running = "RUNNING"
    succeeded = "SUCCEEDED"
    failed = "FAILED"


class BrokerageJobs(Base, ToDict):
    __tablename__ = "brokerage_jobs"
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    user_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(BrokerageJobsStatus), default=BrokerageJobsStatus.pending.value, nullable=False)
    retries = Column(Integer, default=0, nullable=False)
    params = Column(String)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    created_at = Column(DateTime, server_default=UTCNow(), nullable=False)


class Securities(Base, ToDict):
    __tablename__ = "securities"
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    collect = Column(Boolean, default=False, index=True, nullable=False)
    name = Column(String, nullable=False)
    ticker_symbol: str = Column(String, unique=True, nullable=False)
    exchange = Column(String)
    description = Column(String)
    website = Column(String)
    industry = Column(String)
    ceo = Column(String)
    issue_type = Column(String)
    sector = Column(String)
    primary_sic_code = Column(BigInteger)
    employee_count = Column(Integer)
    address = Column(String)
    phone = Column(String)
    open_price = Column(DECIMAL(19, 4), nullable=False)
    close_price = Column(DECIMAL(19, 4), nullable=False)
    type = Column(String)
    currency = Column(String)
    last_updated = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
    created_at = Column(DateTime, server_default=UTCNow())


class SecurityPrices(Base, ToDict):
    __tablename__ = "security_prices"
    __table_args__ = (UniqueConstraint("price_time", "security_id"),)
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False)
    security_id = Column(Integer, ForeignKey("securities.id"), nullable=False)
    price = Column(DECIMAL(19, 4), nullable=False)
    price_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())
