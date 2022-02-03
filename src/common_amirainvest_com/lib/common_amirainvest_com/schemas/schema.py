import datetime
import enum
import typing as t
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
    ForeignKey,
    Integer,
    String,
    text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime


Base = declarative_base()


class UTCNow(expression.FunctionElement):  # type: ignore[name-defined]
    type = DateTime()


@compiles(UTCNow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


def generate_uuid_string() -> str:
    return str(uuid.uuid4())


class Info(BaseModel):
    default: t.Union[bool, str, uuid.UUID, int, datetime.datetime]
    generator: t.Optional[t.Callable]


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


class Users(Base, ToDict):
    __tablename__ = "users"
    id: str = Column(
        UUID(as_uuid=False),
        primary_key=True,
        unique=True,
        default=generate_uuid_string,
        server_default=text("uuid_generate_v4()"),
    )

    benchmark = Column(Integer, ForeignKey("securities.id"), nullable=False)

    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)

    sub = Column(String, nullable=False, info=Info(default="fake_sub").dict())

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    bio = Column(String)
    chip_labels = Column(ARRAY(String))
    deleted_at = Column(DateTime)
    interests_diversification_rating = Column(Integer)
    linkedin_profile = Column(String)
    personal_site_url = Column(String)
    picture_url = Column(String)
    public_holdings = Column(Boolean)
    public_performance = Column(Boolean)
    public_profile = Column(Boolean)
    public_trades = Column(Boolean)
    trading_strategies = Column(ARRAY(String))

    created_at = Column(DateTime, server_default=UTCNow())
    email_verified = Column(Boolean, server_default=expression.false())
    is_claimed = Column(Boolean, server_default=expression.false())
    is_deactivated = Column(Boolean, server_default=expression.false())
    is_deleted = Column(Boolean, server_default=expression.false())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class UsersModel(BaseModel):
    # TODO Change this be the same as table
    id: str

    email: str
    username: str

    sub: Optional[str]

    first_name: str
    last_name: str

    # benchmark = Column(String)
    # bio = Column(String)
    # chip_labels = Column(ARRAY(String))
    # deleted_at = Column(DateTime)
    # interests_diversification_rating = Column(Integer)
    # linkedin_profile = Column(String)
    # personal_site_url = Column(String)
    # picture_url = Column(String)
    # public_holdings = Column(Boolean)
    # public_performance = Column(Boolean)
    # public_profile = Column(Boolean)
    # public_trades = Column(Boolean)
    # trading_strategies = Column(ARRAY(String))
    #
    # created_at = Column(DateTime, server_default=UTCNow())
    # email_verified = Column(Boolean, server_default=expression.false())
    # is_claimed = Column(Boolean, server_default=expression.false())
    # is_deactivated = Column(Boolean, server_default=expression.false())
    # is_deleted = Column(Boolean, server_default=expression.false())
    # updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


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
    id = Column(Integer, primary_key=True, unique=True)

    user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    platform = Column(Enum(MediaPlatform), nullable=False)
    first_error_at = Column(String, nullable=False)

    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class UserFeedback(Base, ToDict):
    __tablename__ = "user_feedback"
    id = Column(Integer, primary_key=True, unique=True)

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
    id = Column(Integer, primary_key=True, autoincrement=True)

    username = Column(String, nullable=False)
    creator_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    is_deleted = Column(Boolean, server_default=expression.false())
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class SubstackArticles(Base, ToDict):
    __tablename__ = "substack_articles"
    article_id = Column(String, primary_key=True, unique=True, nullable=False)

    substack_user = Column(Integer, ForeignKey("substack_users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)

    url = Column(String)

    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class YouTubers(Base, ToDict):
    __tablename__ = "youtubers"
    channel_id = Column(String, primary_key=True, unique=True)

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
    video_id = Column(String, primary_key=True, unique=True)

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
    twitter_user_id = Column(String, primary_key=True, unique=True)

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
    tweet_id = Column(String, primary_key=True, unique=True)

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

    platform = Column(Enum(MediaPlatform), nullable=False)

    chip_labels = Column(ARRAY(String))
    html = Column(String)
    photos = Column(ARRAY(String))
    platform_post_id = Column(String)
    platform_user_id = Column(String)
    profile_img_url = Column(String)
    profile_url = Column(String)
    text = Column(String)
    title = Column(String)

    created_at = Column(DateTime, server_default=UTCNow())
    subscription_level = Column(Enum(SubscriptionLevel), server_default=SubscriptionLevel.standard.value)
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class PostsModel(BaseModel):
    id: int

    creator_id: str

    platform: str

    chip_labels: Optional[List[str]]
    html: Optional[str]
    photos: Optional[List[str]]
    platform_post_id: Optional[str]
    platform_user_id: Optional[str]
    profile_img_url: Optional[str]
    profile_url: Optional[str]
    text: Optional[str]
    title: Optional[str]

    created_at: Optional[datetime.datetime]
    subscription_level: SubscriptionLevel = SubscriptionLevel.standard
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


class FinancialInstitutions(Base, ToDict):
    __tablename__ = "financial_institutions"
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)

    plaid_id = Column(String, unique=True)
    third_party_institution_id = Column(String, unique=True)

    name = Column(String, nullable=False)

    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class PlaidItems(Base, ToDict):
    __tablename__ = "plaid_items"
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)

    user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)

    plaid_item_id = Column(String, unique=True, nullable=False)

    institution_id = Column(Integer, ForeignKey("financial_institutions.id"))


class FinancialAccounts(Base, ToDict):
    __tablename__ = "financial_accounts"
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)

    user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    plaid_item_id = Column(Integer, ForeignKey("plaid_items.id"), nullable=False)

    plaid_id = Column(String, unique=True, nullable=False)

    available_to_withdraw = Column(DECIMAL(19, 4))
    current_funds = Column(DECIMAL(19, 4))
    iso_currency_code = Column(String)
    limit = Column(DECIMAL(19, 4))
    mask = Column(String)
    official_account_name = Column(String)
    sub_type = Column(String)
    type = Column(String)
    unofficial_currency_code = Column(String)
    user_assigned_account_name = Column(String)

    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class FinancialAccountTransactions(Base, ToDict):
    __tablename__ = "financial_account_transactions"
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)

    account_id = Column(Integer, ForeignKey("financial_accounts.id"), nullable=False)
    security_id = Column(Integer, ForeignKey("plaid_securities.id"))

    plaid_investment_transaction_id = Column(String, unique=True, nullable=False)

    name = Column(String, nullable=False)
    posting_date = Column(DateTime, nullable=False)
    price = Column(DECIMAL(19, 4), nullable=False)
    quantity = Column(DECIMAL, nullable=False)
    subtype = Column(String, nullable=False)
    type = Column(String, nullable=False)
    value_amount = Column(DECIMAL(19, 4), nullable=False)

    fees = Column(DECIMAL(19, 4))
    iso_currency_code = Column(String)
    unofficial_currency_code = Column(String)

    created_at = Column(DateTime, server_default=UTCNow())


class FinancialAccountCurrentHoldings(Base, ToDict):
    __tablename__ = "financial_account_current_holdings"
    __table_args__ = (UniqueConstraint("account_id", "plaid_security_id"),)
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)

    account_id = Column(Integer, ForeignKey("financial_accounts.id"), nullable=False)
    plaid_security_id = Column(Integer, ForeignKey("plaid_securities.id"), nullable=False)
    user_id: str = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)

    institution_value = Column(DECIMAL(19, 4), nullable=False)
    latest_price = Column(DECIMAL(19, 4), nullable=False)
    quantity = Column(DECIMAL(19, 4), nullable=False)

    cost_basis = Column(DECIMAL(19, 4))
    iso_currency_code = Column(String)
    latest_price_date = Column(DateTime)
    unofficial_currency_code = Column(String)

    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class PlaidSecurities(Base, ToDict):
    __tablename__ = "plaid_securities"
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)

    financial_institution_id = Column(Integer, ForeignKey("financial_institutions.id"))

    plaid_security_id = Column(String, unique=True)
    ticker_symbol = Column(String, unique=True)

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

    plaid_securities_id = Column(Integer, ForeignKey("plaid_securities.id"), nullable=False)

    price = Column(DECIMAL(19, 4), nullable=False)
    price_time = Column(DateTime, nullable=False)

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
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)

    collect = Column(Boolean, default=False, server_default=expression.false(), index=True)
    is_benchmark = Column(Boolean, default=False, server_default=expression.false(), index=True)

    human_readable_name = Column(String, unique=True, info={"note": "This is manually populated for benchmarks"})
    ticker_symbol: str = Column(String, unique=True, nullable=False)

    close_price = Column(DECIMAL(19, 4), nullable=False)
    name = Column(String, nullable=False)
    open_price = Column(DECIMAL(19, 4), nullable=False)

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


class SecurityPrices(Base, ToDict):
    __tablename__ = "security_prices"
    __table_args__ = (UniqueConstraint("security_id", "price_time"),)
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)

    security_id = Column(Integer, ForeignKey("securities.id"), nullable=False)

    price = Column(DECIMAL(19, 4), nullable=False)
    price_time = Column(DateTime, nullable=False)

    created_at = Column(DateTime, server_default=UTCNow())


class TradingStrategies(Base, ToDict):
    __tablename__ = "trading_strategies"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String, nullable=False)


class ChipLabels(Base, ToDict):
    __tablename__ = "chip_labels"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String, nullable=False)
