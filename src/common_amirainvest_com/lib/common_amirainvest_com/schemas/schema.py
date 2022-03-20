import datetime
import decimal
import enum
import typing as t
import uuid
from decimal import Decimal
from typing import List, Optional

import faker
from pydantic import BaseModel
from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    Column,
    DECIMAL,
    Enum,
    ForeignKey,
    func,
    Index,
    Integer,
    String,
    text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import expression
from sqlalchemy.types import Date, DateTime


Base = declarative_base()

fake = faker.Faker()


class UTCNow(expression.FunctionElement):  # type: ignore[name-defined]
    type = DateTime()


@compiles(UTCNow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


def generate_uuid_string() -> str:
    return str(uuid.uuid4())


class FactoryInfo(BaseModel):
    default: t.Union[bool, str, uuid.UUID, int, datetime.datetime]
    generator: t.Optional[t.Tuple[t.Callable, t.Any]]


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


class SubscriptionLevel(enum.Enum):
    standard = "standard"
    premium = "premium"


class ClaimablePlatform(enum.Enum):
    youtube = "youtube"
    substack = "substack"
    twitter = "twitter"


class MediaPlatform(enum.Enum):
    youtube = "youtube"
    substack = "substack"
    twitter = "twitter"
    brokerage = "brokerage"
    amira = "amira"


class JobsStatus(enum.Enum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class NotificationTypes(enum.Enum):
    trade = "trade"
    creator_join = "creator_joined"
    amira_post = "amira_post"
    mention = "mention"
    upvote = "upvote"
    watchlist_price = "watchlist_price_movement"
    shared_change = "shared_watchlist_change"
    shared_price = "shared_watchlist_price_movement"


class FinancialAccountStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    error = "error"


class Users(Base, ToDict):
    __tablename__ = "users"
    id: str = Column(
        UUID(as_uuid=False),
        primary_key=True,
        unique=True,
        default=generate_uuid_string,
        server_default=text("uuid_generate_v4()"),
    )

    benchmark = Column(Integer, ForeignKey("securities.id"), nullable=True)

    email = Column(
        String,
        unique=True,
        nullable=False,
        info={"factory": FactoryInfo(default="", generator=(fake.unique.email, None)).dict()},
    )
    username = Column(
        String,
        unique=True,
        nullable=False,
        info={"factory": FactoryInfo(default="", generator=(fake.unique.name, None)).dict()},
    )

    sub = Column(
        String,
        nullable=False,
        info={"factory": FactoryInfo(default="", generator=(fake.unique.name, None)).dict()},
    )

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    bio = Column(String)
    chip_labels = Column(ARRAY(String))
    deleted_at = Column(DateTime)
    interests_diversification_rating = Column(Integer)
    linkedin_profile = Column(String)
    personal_site_url = Column(String)
    picture_url = Column(String)
    public_holdings_activate = Column(Boolean, nullable=False, default=False, server_default=expression.false())
    public_performance_activate = Column(Boolean, nullable=False, default=False, server_default=expression.false())
    public_profile_deactivate = Column(Boolean, nullable=False, default=False, server_default=expression.false())
    public_trades_activate = Column(Boolean, nullable=False, default=False, server_default=expression.false())
    trading_strategies = Column(ARRAY(String))

    created_at = Column(DateTime, server_default=UTCNow())
    email_verified = Column(Boolean, server_default=expression.false())
    is_claimed = Column(Boolean, server_default=expression.false())
    is_deactivated = Column(Boolean, server_default=expression.false())
    is_deleted = Column(Boolean, server_default=expression.false())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class UsersModel(BaseModel):
    class Config:
        orm_mode = True

    id: str

    email: str
    username: str

    sub: Optional[str]

    first_name: str
    last_name: str

    bio: Optional[str]
    benchmark: Optional[int]
    chip_labels: Optional[list[str]]
    deleted_at: Optional[datetime.datetime]
    interests_diversification_rating: Optional[int]
    linkedin_profile: Optional[str]
    personal_site_url: Optional[str]
    picture_url: Optional[str]
    public_holdings_activate: Optional[bool]
    public_performance_activate: Optional[bool]
    public_profile_deactivate: Optional[bool]
    public_trades_activate: Optional[bool]
    trading_strategies: Optional[list[str]]

    created_at: Optional[datetime.datetime]
    email_verified: Optional[bool]
    is_claimed: Optional[bool]
    is_deactivated: Optional[bool]
    is_deleted: Optional[bool]
    updated_at: Optional[datetime.datetime]


class BroadcastRequests(Base, ToDict):
    """
    If a user wants a creator join amira
    """

    __tablename__ = "broadcast_requests"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    subscriber_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creator_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, server_default=UTCNow())


class BroadcastRequestsModel(BaseModel):
    id: int

    subscriber_id: str
    creator_id: str

    created_at: Optional[datetime.datetime]


class UserSubscriptions(Base, ToDict):
    __tablename__ = "user_subscriptions"
    __table_args__ = (UniqueConstraint("subscriber_id", "creator_id", name="uq_user_sub"),)
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    subscriber_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creator_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # TODO remove this from update endpoint
    subscription_level = Column(
        Enum(SubscriptionLevel), server_default=SubscriptionLevel.standard.value, nullable=False
    )

    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
    is_deleted = Column(Boolean, server_default=expression.false())


class UserSubscriptionsModel(BaseModel):
    id: int

    subscriber_id: str
    creator_id: str
    subscription_level: SubscriptionLevel

    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    is_deleted: Optional[bool] = False


class UserMediaErrors(Base, ToDict):
    __tablename__ = "user_media_errors"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    platform = Column(Enum(MediaPlatform), nullable=False)
    first_error_at = Column(String, nullable=False)

    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class UserFeedback(Base, ToDict):
    __tablename__ = "user_feedback"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)  # TODO change char limit in app

    created_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class UserFeedbackModel(BaseModel):
    id: int

    user_id: str
    text: str

    created_at: Optional[datetime.datetime]


class SubstackUsers(Base, ToDict):
    __tablename__ = "substack_users"
    username = Column(String, primary_key=True, nullable=False, unique=True, autoincrement=False)
    creator_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    is_deleted = Column(Boolean, server_default=expression.false())
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class SubstackArticles(Base, ToDict):
    __tablename__ = "substack_articles"
    article_id = Column(String, primary_key=True, unique=True, nullable=False, autoincrement=False)

    username = Column(String, ForeignKey("substack_users.username", ondelete="CASCADE"), nullable=False)

    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)

    url = Column(String)

    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class YouTubers(Base, ToDict):
    __tablename__ = "youtubers"
    channel_id = Column(String, primary_key=True, unique=True, autoincrement=False)

    creator_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    channel_username = Column(String)
    description = Column(String)
    profile_img_url = Column(String)
    subscriber_count = Column(Integer)
    title = Column(String)
    video_count = Column(Integer)

    is_deleted = Column(Boolean, server_default=expression.false())
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class YouTubeVideos(Base, ToDict):
    __tablename__ = "youtube_videos"
    video_id = Column(String, primary_key=True, unique=True, autoincrement=False)

    channel_id = Column(String, ForeignKey("youtubers.channel_id", ondelete="CASCADE"))

    published_at = Column(DateTime, nullable=False)

    embed_url = Column(String)
    playlist_id = Column(String)
    title = Column(String)
    video_url = Column(String)

    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class TwitterUsers(Base, ToDict):
    __tablename__ = "twitter_users"
    twitter_user_id = Column(String, primary_key=True, unique=True, autoincrement=False)

    creator_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    username = Column(String, nullable=False)

    follower_count = Column(Integer)
    following_count = Column(Integer)
    name = Column(String)
    profile_img_url = Column(String)
    profile_url = Column(String)
    tweet_count = Column(Integer)

    is_deleted = Column(Boolean, server_default=expression.false())
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class Tweets(Base, ToDict):
    __tablename__ = "tweets"
    tweet_id = Column(String, primary_key=True, unique=True, autoincrement=False)

    twitter_user_id = Column(String, ForeignKey("twitter_users.twitter_user_id", ondelete="CASCADE"))

    embed = Column(String)
    language = Column(String)
    like_count = Column(Integer)
    possibly_sensitive = Column(Boolean)
    quote_count = Column(Integer)
    reply_count = Column(Integer)
    retweet_count = Column(Integer)
    text = Column(String)
    tweet_url = Column(String)

    created_at = Column(DateTime, server_default=UTCNow())


class TweetAnnotations(Base, ToDict):
    __tablename__ = "tweet_annotations"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=False)

    tweet_id = Column(String, ForeignKey("tweets.tweet_id", ondelete="CASCADE"), unique=True)

    annotation_type = Column(String)
    end = Column(Integer)
    normalized_text = Column(String)
    probability = Column(Integer)
    start = Column(Integer)


class TweetCashtags(Base, ToDict):
    __tablename__ = "tweet_cashtags"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=False)

    tweet_id = Column(String, ForeignKey("tweets.tweet_id", ondelete="CASCADE"), unique=True)

    end = Column(Integer)
    start = Column(Integer)
    tag = Column(String)


class TweetHashtags(Base, ToDict):
    __tablename__ = "tweet_hashtags"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=False)

    tweet_id = Column(String, ForeignKey("tweets.tweet_id", ondelete="CASCADE"), unique=True)

    end = Column(Integer)
    start = Column(Integer)
    tag = Column(String)


class TweetMentions(Base, ToDict):
    __tablename__ = "tweet_mentions"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=False)

    tweet_id = Column(String, ForeignKey("tweets.tweet_id", ondelete="CASCADE"), unique=True)

    start = Column(Integer)
    end = Column(Integer)
    username = Column(String)


class TweetURLs(Base, ToDict):
    __tablename__ = "tweet_urls"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=False)

    tweet_id = Column(String, ForeignKey("tweets.tweet_id", ondelete="CASCADE"), unique=True)

    description = Column(String)
    display_url = Column(String)
    end = Column(Integer)
    expanded_url = Column(String)
    images = Column(String)
    start = Column(Integer)
    status = Column(Integer)
    title = Column(String)
    unwound_url = Column(String)
    url = Column(String)


class Posts(Base, ToDict):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    creator_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    subscription_level = Column(Enum(SubscriptionLevel), server_default=SubscriptionLevel.standard.value)

    title = Column(String)
    content = Column(String)
    photos = Column(ARRAY(String))

    platform = Column(Enum(MediaPlatform), nullable=False)
    platform_display_name = Column(String)
    platform_user_id = Column(String)
    platform_img_url = Column(String)
    platform_profile_url = Column(String)
    twitter_handle = Column(String)

    platform_post_id = Column(String)
    platform_post_url = Column(String)

    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class PostsModel(BaseModel):
    class Config:
        orm_mode = True

    id: int

    creator_id: str
    subscription_level: SubscriptionLevel = SubscriptionLevel.standard

    title: Optional[str]
    content: Optional[str]
    photos: Optional[List[str]]

    platform: MediaPlatform
    platform_display_name: Optional[str]
    platform_user_id: Optional[str]
    platform_img_url: Optional[str]
    platform_profile_url: Optional[str]
    twitter_handle: Optional[str]

    platform_post_id: Optional[str]
    platform_post_url: Optional[str]

    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


# class PostLikes(Base, ToDict):
#     __tablename__ = "post_likes"
#     user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
#     post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
#     liked_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
#
#     post: Posts = relationship(
#         "Posts", backref="liked_post", passive_deletes=True, cascade="all,delete", foreign_keys=[post_id]
#     )
#     user: Users = relationship(
#         "Users", backref="post_liker", passive_deletes=True, cascade="all,delete", foreign_keys=[user_id]
#     )


# class PostComments(Base, ToDict):
# __tablename__ = "post_comments"
# id = Column(Integer, primary_key=True, unique=True)
# user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
# post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
# text = Column(String, nullable=False)
# created_at = Column(DateTime, server_default=UTCNow())
# updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
#
# post: Posts = relationship(
#     "Posts", backref="commented_post", passive_deletes=True, cascade="all,delete", foreign_keys=[post_id]
# )
# user: Users = relationship(
#     "Users", backref="post_commenter", passive_deletes=True, cascade="all,delete", foreign_keys=[user_id]
# )


# class PostReads(Base, ToDict):
#     __tablename__ = "post_reads"
#     id = Column(Integer, primary_key=True, unique=True)
#     user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
#     read_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
#     time_read_seconds = Column(Float, nullable=False)
#
#     post: Posts = relationship(
#         "Posts", backref="read_post", passive_deletes=True, cascade="all,delete", foreign_keys=[post_id]
#     )
#     user: Users = relationship(
#         "Users", backref="post_reader", passive_deletes=True, cascade="all,delete", foreign_keys=[user_id]
#     )


class Bookmarks(Base, ToDict):
    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("user_id", "post_id"),)
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, server_default=UTCNow())
    is_deleted = Column(Boolean, server_default=expression.false())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
    # TODO check how this delete works
    # TODO when adding a bookmark check if it already exists, if it does change is_deleted don't add a new one


class BookmarkModel(BaseModel):
    id: int

    user_id: str
    post_id: int

    created_at: Optional[datetime.datetime]
    is_deleted: Optional[bool] = False
    updated_at: Optional[datetime.datetime]


class HuskRequests(Base, ToDict):
    __tablename__ = "husk_requests"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    requestor_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    platform = Column(Enum(MediaPlatform), nullable=False)
    platform_id = Column(String, nullable=False)
    provided_name = Column(String, nullable=False)

    created_at = Column(DateTime, server_default=UTCNow())
    fulfilled = Column(Boolean, server_default=expression.false())


class HuskRequestsModel(BaseModel):
    id: int

    requestor_id: str

    platform: MediaPlatform
    platform_id: str
    provided_name: str

    created_at: Optional[datetime.datetime]
    fulfilled: Optional[bool]


class Watchlists(Base, ToDict):
    __tablename__ = "watchlists"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    creator_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class WatchlistsModel(BaseModel):
    id: int
    creator_id: str
    name: str
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class WatchlistItems(Base, ToDict):
    __tablename__ = "watchlist_items"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False)
    ticker = Column(String, nullable=False)
    note = Column(String)
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class WatchlistItemsModel(BaseModel):
    id: int
    watchlist_id: int
    ticker: str
    note: Optional[str]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class WatchlistFollows(Base, ToDict):
    __tablename__ = "watchlist_follows"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    follower_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class WatchlistFollowsModel(BaseModel):
    id: int
    follower_id: str
    watchlist_id: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class FinancialInstitutions(Base, ToDict):
    __tablename__ = "financial_institutions"
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)

    plaid_id = Column(String, unique=True)
    third_party_institution_id = Column(String, unique=True)

    name = Column(String, nullable=False)

    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class PlaidItems(Base, ToDict):
    __tablename__ = "plaid_items"
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)

    user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)

    plaid_item_id = Column(String, unique=True, nullable=False)

    institution_id = Column(Integer, ForeignKey("financial_institutions.id"))


class FinancialAccounts(Base, ToDict):
    __tablename__ = "financial_accounts"
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)

    user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    plaid_item_id = Column(BigInteger, ForeignKey("plaid_items.id"), nullable=False)

    plaid_id = Column(String, unique=True, nullable=False)

    status = Column(Enum(FinancialAccountStatus), server_default=FinancialAccountStatus.active.value, nullable=True)

    error_message = Column(String)
    available_to_withdraw = Column(DECIMAL(19, 4))
    current_funds = Column(DECIMAL(19, 4))
    iso_currency_code = Column(String)
    limit = Column(DECIMAL(19, 4))
    mask = Column(String)
    official_account_name = Column(String)
    type = Column(String)
    sub_type = Column(String)
    unofficial_currency_code = Column(String)
    user_assigned_account_name = Column(String)

    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class FinancialAccountTransactions(Base, ToDict):
    __tablename__ = "financial_account_transactions"
    id: int = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)

    account_id: int = Column(BigInteger, ForeignKey("financial_accounts.id"), nullable=False)
    plaid_security_id: int = Column(BigInteger, ForeignKey("plaid_securities.id"))

    plaid_investment_transaction_id = Column(String, unique=True, nullable=False)

    name = Column(String, nullable=False)
    posting_date = Column(TIMESTAMP(timezone=True), nullable=False)
    price: decimal.Decimal = Column(DECIMAL(19, 4), nullable=False)
    quantity: Decimal = Column(DECIMAL, nullable=False)
    type: str = Column(String, nullable=False)
    subtype: str = Column(String, nullable=False)
    value_amount: decimal.Decimal = Column(DECIMAL(19, 4), nullable=False)

    fees = Column(DECIMAL(19, 4))
    iso_currency_code = Column(String)
    unofficial_currency_code = Column(String)

    created_at = Column(DateTime, server_default=UTCNow())


class FinancialAccountCurrentHoldings(Base, ToDict):
    __tablename__ = "financial_account_current_holdings"
    __table_args__ = (UniqueConstraint("account_id", "plaid_security_id"),)
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)

    account_id: int = Column(BigInteger, ForeignKey("financial_accounts.id"), nullable=False)
    plaid_security_id: int = Column(BigInteger, ForeignKey("plaid_securities.id"), nullable=False)

    institution_value = Column(DECIMAL(19, 4), nullable=False)
    latest_price: decimal.Decimal = Column(DECIMAL(19, 4), nullable=False)
    quantity: decimal.Decimal = Column(DECIMAL(19, 4), nullable=False)

    cost_basis = Column(DECIMAL(19, 4))
    iso_currency_code = Column(String)
    latest_price_date = Column(TIMESTAMP(timezone=True))
    unofficial_currency_code = Column(String)

    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class FinancialAccountHoldingsHistory(Base, ToDict):
    __tablename__ = "financial_account_holdings_history"
    __table_args__ = (UniqueConstraint("account_id", "security_id", "holding_date"),)

    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)

    account_id: int = Column(BigInteger, ForeignKey("financial_accounts.id"), nullable=False)
    plaid_security_id: int = Column(BigInteger, ForeignKey("plaid_securities.id"), nullable=False)
    security_id: Optional[int] = Column(BigInteger, ForeignKey("securities.id"))

    price: Decimal = Column(DECIMAL(19, 4), nullable=False)
    quantity: Decimal = Column(DECIMAL(19, 4), nullable=False)
    holding_date = Column(Date, nullable=False)
    cost_basis = Column(DECIMAL(19, 4))

    buy_date = Column(Date, nullable=False)


class PlaidSecurities(Base, ToDict):
    __tablename__ = "plaid_securities"
    id: int = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)

    financial_institution_id: Optional[int] = Column(BigInteger, ForeignKey("financial_institutions.id"))

    plaid_security_id: Optional[str] = Column(String, unique=True)

    security_id: Optional[int] = Column(BigInteger, ForeignKey("securities.id"))

    ticker_symbol = Column(
        String, unique=True, info={"factory": FactoryInfo(default="", generator=(fake.unique.name, None)).dict()}
    )

    name = Column(String, nullable=False)

    cusip = Column(String)
    is_cash_equivalent = Column(Boolean)
    isin = Column(String)
    iso_currency_code = Column(String)
    plaid_institution_security_id = Column(String)
    sedol = Column(String)
    type = Column(String)
    unofficial_currency_code = Column(String)

    created_at = Column(DateTime, server_default=UTCNow())
    last_updated = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class PlaidSecurityPrices(Base, ToDict):
    __tablename__ = "plaid_security_prices"
    __table_args__ = (UniqueConstraint("price_time", "plaid_securities_id"),)
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)

    plaid_securities_id = Column(BigInteger, ForeignKey("plaid_securities.id"), nullable=False)

    price = Column(DECIMAL(19, 4), nullable=False)
    price_time: datetime.datetime = Column(TIMESTAMP(timezone=True), nullable=False)

    created_at = Column(DateTime, server_default=UTCNow())


class BrokerageJobs(Base, ToDict):
    __tablename__ = "brokerage_jobs"
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)

    user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(JobsStatus), server_default=JobsStatus.pending.value, nullable=False)

    retries = Column(Integer, server_default="0", nullable=False)

    ended_at = Column(DateTime)
    error = Column(String)
    params = Column(JSONB)
    started_at = Column(DateTime)

    created_at = Column(DateTime, server_default=UTCNow())


class Securities(Base, ToDict):
    __tablename__ = "securities"
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)

    ticker_symbol: str = Column(
        String,
        unique=True,
        nullable=False,
        info={"factory": FactoryInfo(default="", generator=(fake.unique.name, None)).dict()},
    )

    name = Column(String, nullable=False)
    close_price = Column(DECIMAL(19, 4), nullable=False)
    open_price = Column(DECIMAL(19, 4), nullable=False)

    human_readable_name = Column(String, info={"note": "Remove after deploy"})
    benchmark_alias = Column(String, unique=True, info={"note": "This is manually populated for benchmarks"})

    collect = Column(Boolean, default=False, server_default=expression.false(), index=True)
    is_benchmark = Column(Boolean, default=False, server_default=expression.false(), index=True)

    search_name = Column(String)

    founding_date = Column(Date)
    asset_type = Column(String)
    address = Column(String)
    ceo = Column(String)
    currency = Column(String)
    description = Column(String)
    employee_count = Column(Integer)
    exchange = Column(String)
    industry = Column(String)
    issue_type = Column(String)
    phone = Column(String)
    primary_sic_code = Column(BigInteger)
    sector = Column(String)
    type = Column(String)
    website = Column(String)

    created_at = Column(DateTime, server_default=UTCNow())
    last_updated = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class SecurityInformation(Base, ToDict):
    __tablename__ = "security_information"

    id: int = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)

    security_id: int = Column(BigInteger, ForeignKey("securities.id"), unique=True, nullable=False)

    average_total_volume = Column(DECIMAL(19, 5))
    change = Column(DECIMAL(19, 5))
    change_percentage = Column(DECIMAL(19, 5))
    close = Column(DECIMAL(19, 5))
    close_source = Column(String)
    close_time = Column(Integer)
    currency = Column(String)
    delayed_price = Column(DECIMAL(19, 5))
    delayed_price_time = Column(Integer)
    extended_change = Column(DECIMAL(19, 5))
    extended_change_percentage = Column(DECIMAL(19, 5))
    extended_price = Column(DECIMAL(19, 4))
    extended_price_time = Column(Integer)
    high = Column(DECIMAL(19, 4))
    high_source = Column(String)
    high_time = Column(Integer)
    iex_ask_price = Column(DECIMAL(19, 4))
    iex_ask_size = Column(Integer)
    iex_bid_price = Column(DECIMAL(19, 4))
    iex_bid_size = Column(Integer)
    iex_close = Column(DECIMAL(19, 4))
    iex_close_time = Column(Integer)
    iex_last_updated = Column(Integer)
    iex_market_percentage = Column(DECIMAL(19, 5))
    iex_open = Column(DECIMAL(19, 4))
    iex_open_time = Column(Integer)
    iex_realtime_price = Column(DECIMAL(19, 4))
    iex_real_time_size = Column(DECIMAL(19, 5))
    iex_volume = Column(DECIMAL(19, 4))
    last_trade_time = Column(Integer)
    latest_price = Column(DECIMAL(19, 4))
    latest_source = Column(String)
    latest_time = Column(String)
    latest_update = Column(Integer)
    latest_volume = Column(DECIMAL(19, 5))
    low = Column(DECIMAL(19, 4))
    low_source = Column(String)
    low_time = Column(Integer)
    market_cap = Column(DECIMAL(19, 4))
    odd_lot_delayed_price = Column(DECIMAL(19, 4))
    odd_lot_delayed_price_time = Column(Integer)
    open = Column(DECIMAL(19, 4))
    open_time = Column(Integer)
    open_source = Column(String)
    pe_ratio = Column(DECIMAL(19, 4))
    previous_close = Column(DECIMAL(19, 4))
    previous_volume = Column(DECIMAL(19, 4))
    volume = Column(DECIMAL(19, 4))
    week_high_52 = Column(DECIMAL(19, 4))
    week_low_52 = Column(DECIMAL(19, 4))
    ytd_change = Column(DECIMAL(10, 4))

    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class SecurityPrices(Base, ToDict):
    __tablename__ = "security_prices"
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)

    security_id = Column(BigInteger, ForeignKey("securities.id"), nullable=False)

    price: decimal.Decimal = Column(DECIMAL(19, 4), nullable=False)
    price_time: datetime.datetime = Column(TIMESTAMP(timezone=True), nullable=False)

    created_at = Column(DateTime, server_default=UTCNow())

    __table_args__ = (
        UniqueConstraint("security_id", "price_time"),
        Index("security_prices_price_time_idx", func.brin(price_time), postgresql_using="brin"),
    )


class MarketHolidays(Base, ToDict):
    __tablename__ = "market_holidays"
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    date: datetime.date = Column(Date, unique=True, nullable=False)
    settlement_date: datetime.datetime = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class Notifications(Base, ToDict):
    __tablename__ = "notifications"
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)
    user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notification_type = Column(Enum(NotificationTypes), nullable=False)
    body = Column(JSONB, nullable=False)
    redirect = Column(String, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    profile_url = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class NotificationsModel(BaseModel):
    id: int
    user_id: str
    notification_type: NotificationTypes
    body: dict
    redirect: str
    is_read: Optional[bool]
    is_deleted: Optional[bool]
    profile_url: Optional[str]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class NotificationSettings(Base, ToDict):
    __tablename__ = "notification_settings"
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)
    user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mention = Column(Boolean, default=True, nullable=False)
    upvote = Column(Boolean, default=True, nullable=False)
    watchlist_price = Column(Boolean, default=True, nullable=False)
    shared_change = Column(Boolean, default=True, nullable=False)
    shared_price = Column(Boolean, default=True, nullable=False)
    email_trades = Column(Boolean, default=True, nullable=False)


class NotificationSettingsModel(BaseModel):
    id: int
    user_id: str
    mention: Optional[bool]
    upvote: Optional[bool]
    watchlist_price: Optional[bool]
    shared_change: Optional[bool]
    shared_price: Optional[bool]
    email_trades: Optional[bool]


class TradingStrategies(Base, ToDict):
    __tablename__ = "trading_strategies"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String, nullable=False)


class ChipLabels(Base, ToDict):
    __tablename__ = "chip_labels"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String, nullable=False)


class StripeIdentifiers(Base, ToDict):
    __tablename__ = "stripe_identifiers"
    __table_args__ = (UniqueConstraint("user_id", "stripe_id"),)
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    stripe_id = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())


class PostReports(Base, ToDict):
    __tablename__ = "post_content_reports"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())
