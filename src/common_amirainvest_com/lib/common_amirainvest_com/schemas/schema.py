import datetime
import uuid

from sqlalchemy import BigInteger, Boolean, Column, DECIMAL, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime


__all__ = [
    "Users",
    "BroadcastRequests",
    "Posts",
    "PostLikes",
    "PostComments",
    "PostReads",
    "UserSubscriptions",
    "UserMediaErrors",
    "Bookmarks",
    "SubstackArticles",
    "SubstackUsers",
    "YouTubers",
    "YouTubeVideos",
    "TwitterUsers",
    "Tweets",
    "TweetAnnotations",
    "TweetCashtags",
    "TweetHashtags",
    "TweetMentions",
    "TweetURLs",
    "HuskRequests",
    "FinancialAccounts",
    "FinancialInstitutions",
    "FinancialAccountTransactions",
    "FinancialAccountCurrentHoldings",
    "Securities",
    "SecurityPrices",
]

Base = declarative_base()


class UTCNow(expression.FunctionElement):  # type: ignore[name-defined]
    type = DateTime()


@compiles(UTCNow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class Users(Base):
    __tablename__ = "users"
    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    sub = Column(String, nullable=False)
    name = Column(String, nullable=False)
    bio = Column(String)
    username = Column(String, nullable=False)
    picture_url = Column(String, nullable=False)
    email = Column(String, nullable=False)
    personal_site_url = Column(String)
    linkedin_profile = Column(String)
    email_verified = Column(Boolean, default=False)
    interests_value = Column(Boolean)
    interests_growth = Column(Boolean)
    interests_long_term = Column(Boolean)
    interests_short_term = Column(Boolean)
    interests_diversification_rating = Column(Integer)
    benchmark = Column(String)
    public_profile = Column(Boolean)
    public_performance = Column(Boolean)
    public_holdings = Column(Boolean)
    public_trades = Column(Boolean)
    is_claimed = Column(Boolean)
    is_deactivated = Column(Boolean)
    is_deleted = Column(Boolean)
    # deleted_at = Column(DateTime)
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)


class BroadcastRequests(Base):
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


class UserSubscriptions(Base):
    __tablename__ = "user_subscriptions"
    id = Column(Integer, primary_key=True, unique=True)
    subscriber_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creator_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
    is_deleted = Column(Boolean, nullable=False)

    subscriber: Users = relationship(
        "Users", backref="subscriber", passive_deletes=True, cascade="all,delete", foreign_keys=[subscriber_id]
    )
    creator: Users = relationship(
        "Users", backref="creator", passive_deletes=True, cascade="all,delete", foreign_keys=[creator_id]
    )


class UserMediaErrors(Base):
    __tablename__ = "user_media_errors"
    id = Column(Integer, primary_key=True, unique=True)
    user_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String, nullable=False)
    error_at = Column(String, nullable=False)
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)

    creator: Users = relationship("Users", backref="user_media_errors", passive_deletes=True, cascade="all,delete")


class SubstackUsers(Base):
    __tablename__ = "substack_users"
    username = Column(String, primary_key=True, unique=True)
    user_url = Column(String)
    creator_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_deleted = Column(Boolean)
    created_at = Column(DateTime, server_default=UTCNow())

    creator: Users = relationship("Users", backref="substack_users", passive_deletes=True, cascade="all,delete")


class SubstackArticles(Base):
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


class YouTubers(Base):
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


class YouTubeVideos(Base):
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


class TwitterUsers(Base):
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


class Tweets(Base):
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


class TweetAnnotations(Base):
    __tablename__ = "tweet_annotations"
    id = Column(Integer, primary_key=True, unique=True)
    tweet_id = Column(String, ForeignKey("tweets.tweet_id", ondelete="CASCADE"), unique=True)
    start = Column(Integer)
    end = Column(Integer)
    probability = Column(Integer)
    annotation_type = Column(String)
    normalized_text = Column(String)

    tweet: Tweets = relationship("Tweets", backref="tweet_annotations", passive_deletes=True, cascade="all,delete")


class TweetCashtags(Base):
    __tablename__ = "tweet_cashtags"
    id = Column(Integer, primary_key=True, unique=True)
    tweet_id = Column(String, ForeignKey("tweets.tweet_id", ondelete="CASCADE"), unique=True)
    start = Column(Integer)
    end = Column(Integer)
    tag = Column(String)

    tweet: Tweets = relationship("Tweets", backref="tweet_cashtags", passive_deletes=True, cascade="all,delete")


class TweetHashtags(Base):
    __tablename__ = "tweet_hashtags"
    id = Column(Integer, primary_key=True, unique=True)
    tweet_id = Column(String, ForeignKey("tweets.tweet_id", ondelete="CASCADE"), unique=True)
    start = Column(Integer)
    end = Column(Integer)
    tag = Column(String)

    tweet: Tweets = relationship("Tweets", backref="tweet_hashtags", passive_deletes=True, cascade="all,delete")


class TweetMentions(Base):
    __tablename__ = "tweet_mentions"
    id = Column(Integer, primary_key=True, unique=True)
    tweet_id = Column(String, ForeignKey("tweets.tweet_id", ondelete="CASCADE"), unique=True)
    start = Column(Integer)
    end = Column(Integer)
    username = Column(String)

    tweet: Tweets = relationship("Tweets", backref="tweet_mentions", passive_deletes=True, cascade="all,delete")


class TweetURLs(Base):
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


class Posts(Base):
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
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)

    creator: Users = relationship(
        "Users", backref="post_creator", passive_deletes=True, cascade="all,delete", foreign_keys=[creator_id]
    )


class PostLikes(Base):
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


class PostComments(Base):
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


class PostReads(Base):
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


class Bookmarks(Base):
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


class HuskRequests(Base):
    __tablename__ = "husk_requests"
    id = Column(Integer, primary_key=True, unique=True)
    twitter_user_id = Column(String)
    youtube_channel_id = Column(String)
    substack_username = Column(String)
    created_at = Column(DateTime, server_default=UTCNow())
    fulfilled = Column(Boolean)


class FinancialInstitutions(Base):
    __tablename__ = "financial_institutions"
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    plaid_id = Column(String, unique=True)
    third_party_institution_id = Column(String, unique=True)
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
    created_at = Column(DateTime, server_default=UTCNow())


class FinancialAccounts(Base):
    __tablename__ = "financial_accounts"
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    user_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
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


class FinancialAccountTransactions(Base):
    __tablename__ = "financial_account_transactions"
    __table_args__ = (UniqueConstraint("account_id", "security_id", "posting_date"),)
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


class FinancialAccountCurrentHoldings(Base):
    __tablename__ = "financial_account_current_holdings"
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False)
    account_id = Column(Integer, ForeignKey("financial_accounts.id"), nullable=False)
    security_id = Column(Integer, ForeignKey("securities.id"), nullable=False)
    latest_price = Column(DECIMAL(19, 4), nullable=False)
    latest_price_date = Column(DateTime)
    institution_value = Column(DECIMAL(19, 4), nullable=False)
    cost_basis = Column(DECIMAL(19, 4))
    updated_at = Column(DateTime, server_default=UTCNow(), onupdate=datetime.datetime.utcnow)
    created_at = Column(DateTime, server_default=UTCNow())
    quantity = Column(DECIMAL(19, 4), nullable=False)
    iso_currency_code = Column(String)
    unofficial_currency_code = Column(String)


class Securities(Base):
    __tablename__ = "securities"
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


class SecurityPrices(Base):
    __tablename__ = "security_prices"
    __table_args__ = (UniqueConstraint("price_time", "securities_id"),)
    id = Column(BigInteger, primary_key=True, unique=True, nullable=False)
    securities_id = Column(Integer, ForeignKey("securities.id"), nullable=False)
    price = Column(DECIMAL(19, 4), nullable=False)
    price_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=UTCNow())
