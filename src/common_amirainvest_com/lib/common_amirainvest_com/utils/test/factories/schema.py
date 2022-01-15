"""
https://factoryboy.readthedocs.io/en/stable/orms.html#sqlalchemy
https://factoryboy.readthedocs.io/en/stable/index.html
"""
import factory

from common_amirainvest_com.schemas.schema import (
    Bookmarks,
    BroadcastRequests,
    HuskRequests,
    Posts,
    SubstackArticles,
    SubstackUsers,
    Tweets,
    TwitterUsers,
    UserFeedback,
    UserMediaErrors,
    Users,
    UserSubscriptions,
    YouTubers,
    YouTubeVideos,
)
from common_amirainvest_com.utils.test.factories.base import FactoryBase


class UsersFactory(FactoryBase):
    class Meta:
        model = Users

    sub = factory.Faker("name")
    name = "Test Name"
    username = "Test Username"
    picture_url = "https://test.com"
    email = "test@test.com"
    email_verified = True
    is_deleted = False


class UserFeedbackFactory(FactoryBase):
    class Meta:
        model = UserFeedback

    user_id = ""


class HuskRequestsFactory(FactoryBase):
    class Meta:
        model = HuskRequests


class PostsFactory(FactoryBase):
    class Meta:
        model = Posts

    creator_id = ""
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
