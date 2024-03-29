"""
https://factoryboy.readthedocs.io/en/stable/orms.html#sqlalchemy
https://factoryboy.readthedocs.io/en/stable/index.html
"""
import factory

from common_amirainvest_com.schemas.schema import (
    Bookmarks,
    BroadcastRequests,
    ChipLabels,
    HuskRequests,
    Posts,
    Securities,
    SubstackArticles,
    SubstackUsers,
    TradingStrategies,
    Tweets,
    TwitterUsers,
    UserFeedback,
    UserMediaErrors,
    Users,
    UserSubscriptions,
    WatchlistFollows,
    Watchlists,
    YouTubers,
    YouTubeVideos,
)
from common_amirainvest_com.utils.test.factories.base import FactoryBase


class WatchlistsFollowsFactory(FactoryBase):
    class Meta:
        model = WatchlistFollows

    follower_id = ""
    watchlist_id = ""


class WatchlistsFactory(FactoryBase):
    class Meta:
        model = Watchlists

    creator_id = ""
    name = ""
    tickers = ["APPL", "TSLA"]


class TradingStrategiesFactory(FactoryBase):
    class Meta:
        model = TradingStrategies


class ChipLabelsFactory(FactoryBase):
    class Meta:
        model = ChipLabels


class UsersFactory(FactoryBase):
    class Meta:
        model = Users

    benchmark = 1
    sub = factory.Faker("name")
    first_name = "test_first_name"
    last_name = "test_last_name"
    username = factory.Faker("name")
    picture_url = "https://test.com"
    email = factory.Faker("email")
    email_verified = True
    is_deleted = False


class SecuritiesFactory(FactoryBase):
    class Meta:
        model = Securities

    ticker_symbol = factory.Faker("name")
    name = factory.Faker("name")
    close_price = 0
    open_price = 0


class UserFeedbackFactory(FactoryBase):
    class Meta:
        model = UserFeedback

    user_id = ""


class HuskRequestsFactory(FactoryBase):
    class Meta:
        model = HuskRequests

    provided_name = ""
    platform_id = ""
    platform = "twitter"


class PostsFactory(FactoryBase):
    class Meta:
        model = Posts

    platform = "twitter"


class BroadcastRequestsFactory(FactoryBase):
    class Meta:
        model = BroadcastRequests

    subscriber_id = ""
    creator_id = ""


class UserSubscriptionsFactory(FactoryBase):
    class Meta:
        model = UserSubscriptions

    subscriber_id = ""
    creator_id = ""
    is_deleted = False


class UserMediaErrorsFactory(FactoryBase):
    class Meta:
        model = UserMediaErrors

    user_id = ""


class BookmarksFactory(FactoryBase):
    class Meta:
        model = Bookmarks

    user_id = ""
    post_id = 0
    is_deleted = False


class SubstackArticlesFactory(FactoryBase):
    class Meta:
        model = SubstackArticles

    article_id = ""
    title = ""
    summary = ""
    author = ""


class SubstackUsersFactory(FactoryBase):
    class Meta:
        model = SubstackUsers

    username = ""
    creator_id = ""


class YouTubersFactory(FactoryBase):
    class Meta:
        model = YouTubers

    channel_id = ""
    creator_id = ""


class YouTubeVideosFactory(FactoryBase):
    class Meta:
        model = YouTubeVideos

    video_id = ""
    published_at = ""


class TwitterUsersFactory(FactoryBase):
    class Meta:
        model = TwitterUsers

    creator_id = ""
    username = ""


class TweetsFactory(FactoryBase):
    class Meta:
        model = Tweets

    tweet_id = ""
