import urllib.parse
from datetime import datetime
from typing import Optional

import arrow
import requests
from bs4 import BeautifulSoup

from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from common_amirainvest_com.utils.logger import log
from data_imports_amirainvest_com.consts import TWITTER_API_TOKEN_ENV, TWITTER_API_URL
from data_imports_amirainvest_com.controllers import posts
from data_imports_amirainvest_com.controllers.tweets import create_tweet, get_tweets_for_creator
from data_imports_amirainvest_com.controllers.twitter_users import create_twitter_user
from data_imports_amirainvest_com.platforms.platforms import PlatformUser
from data_imports_amirainvest_com.controllers.users import get_user


HEADERS = {
    "Cache-Control": "no-cache",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Authorization": f"Bearer {TWITTER_API_TOKEN_ENV}",
}
OLDEST_TWEET_WANTED_AGE = 1  # MONTHS
ACCEPTED_ENTITY_TYPES = ["cashtags", "hashtags", "mentions", "annotations", "urls"]


class TwitterUser(PlatformUser):
    def __init__(self, username, creator_id):
        super().__init__()
        self.twitter_user_id: str = ""
        self.creator_id: str = creator_id
        self.name: str = ""
        self.username: str = username
        self.profile_img_url: str = ""
        self.profile_url: str = ""
        self.follower_count: Optional[int] = None
        self.following_count: Optional[int] = None
        self.tweet_count: Optional[int] = None
        self.is_deleted = False
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return f"{self.username}"

    def get_unique_id(self):
        if not self.twitter_user_id:
            self.load_twitter_user_data()
        return self.twitter_user_id

    def load_twitter_user_data(self):
        params = {"user.fields": "profile_image_url,public_metrics"}
        user_data = requests.request(
            "GET",
            f"{TWITTER_API_URL}/2/users/by/username/{self.username}",
            headers=HEADERS,
            params=params,
        ).json()["data"]
        self.twitter_user_id = user_data["id"]
        self.name = user_data["name"]
        self.username = user_data["username"]
        self.profile_img_url = user_data["profile_image_url"]
        self.profile_url = f"https://twitter.com/{self.username}"
        self.follower_count = user_data["public_metrics"]["followers_count"]
        self.following_count = user_data["public_metrics"]["following_count"]
        self.tweet_count = user_data["public_metrics"]["tweet_count"]

    async def get_stored_creator_tweets(self):
        return await get_tweets_for_creator(self.creator_id)

    async def get_last_pulled_tweet_timestamp(self) -> str:
        stored_tweets = await self.get_stored_creator_tweets()
        if stored_tweets:
            time = arrow.get(stored_tweets[0].created_at)
        else:
            time = arrow.utcnow().shift(months=-1)

        return time.format("YYYY-MM-DD[T]HH:mm:ss[Z]")

    async def get_tweets_from_url(self, start_date=None):
        raw_tweets = []
        if not self.twitter_user_id:
            self.load_twitter_user_data()
        params = {
            "start_time": await self.get_last_pulled_tweet_timestamp(),
            "exclude": "retweets,replies",
            "tweet.fields": "attachments,created_at,lang,text,public_metrics,possibly_sensitive,entities",
            "max_results": 100,  # 100 MAX
        }
        tweets_data = self._get_tweets_data(params)
        for raw_tweet_data in tweets_data["data"]:
            raw_tweet_data["twitter_user_id"] = self.twitter_user_id
            raw_tweet_data["twitter_user_username"] = self.username
            raw_tweets.append(raw_tweet_data)
        while "next_token" in tweets_data["meta"]:
            params["pagination_token"] = tweets_data["meta"]["next_token"]
            tweets_data = self._get_tweets_data(params)
            for raw_tweet_data in tweets_data["data"]:
                raw_tweet_data["twitter_user_id"] = self.twitter_user_id
                raw_tweet_data["twitter_user_username"] = self.username
                raw_tweets.append(raw_tweet_data)
        tweets = await self.convert_and_load_tweets(raw_tweets)
        return tweets

    async def convert_and_load_tweets(self, raw_tweets):
        tweets = []
        tweet_posts = []
        stored_tweets = await self.get_stored_creator_tweets()
        stored_tweet_ids = [x.tweet_id for x in stored_tweets]
        user = await get_user(self.creator_id)
        for raw_tweet in raw_tweets:
            if raw_tweet["id"] not in stored_tweet_ids:
                tweets.append(
                    Tweet(
                        **{
                            "twitter_user_id": self.twitter_user_id,
                            "twitter_username": self.username,
                            "tweet_id": raw_tweet.get("id"),
                            "text": raw_tweet.get("text"),
                            "created_at": raw_tweet.get("created_at"),
                            "entities": raw_tweet.get("entities", {}),
                            "language": raw_tweet.get("lang"),
                            "like_count": raw_tweet.get("like_count"),
                            "quote_count": raw_tweet.get("quote_count"),
                            "reply_count": raw_tweet.get("reply_count"),
                            "retweet_count": raw_tweet.get("retweet_count"),
                            "tweet_url": f"https://twitter.com/{self.username}/status/{raw_tweet.get('id')}",
                        }
                    )
                )
                tweet_posts.append(
                    {
                        "creator_id": self.creator_id,
                        "platform": "twitter",
                        "platform_user_id": self.twitter_user_id,
                        "platform_post_id": raw_tweet.get("id"),
                        "profile_img_url": "",
                        "text": raw_tweet.get("text"),
                        "html": "",
                        "title": "",
                        "profile_url": "",
                        "chip_labels": user.chip_labels,
                        "created_at": raw_tweet.get("created_at"),
                        "updated_at": raw_tweet.get("created_at"),
                    }
                )
        return tweets, tweet_posts

    def _get_tweets_data(self, params: dict) -> dict:
        return requests.request(
            "GET",
            f"{TWITTER_API_URL}/2/users/{self.twitter_user_id}/tweets",
            headers=HEADERS,
            params=params,
        ).json()

    async def load_platform_data(self):
        self.load_twitter_user_data()
        tweets, tweet_posts = await self.get_tweets_from_url()
        twitter_user_exists = await self.get_user_platform_pair_exists("twitter", self.get_unique_id())
        if not twitter_user_exists:
            log.info(f"Added new Twitter user: {self.username}")
            await create_twitter_user(self.__dict__)
        if tweets:
            for tweet in tweets:
                await create_tweet(tweet.__dict__)
            for tweet_post in tweet_posts:
                await posts.create_post(tweet_post)
                posts.put_post_on_creators_redis_feeds(tweet_post)
                await posts.put_post_on_subscriber_redis_feeds(tweet_post)


class Tweet:
    def __init__(
        self,
        twitter_user_id,
        twitter_username,
        tweet_id,
        text,
        created_at,
        entities,
        language,
        like_count,
        quote_count,
        reply_count,
        retweet_count,
        tweet_url,
    ):
        self.twitter_user_id: str = twitter_user_id
        self.twitter_username: str = twitter_username
        self.tweet_id: str = tweet_id
        self.text: str = text
        self.created_at: datetime = created_at
        self.entities: dict = entities
        self.language: str = language
        self.possibly_sensitive: bool = False
        self.like_count: int = like_count
        self.quote_count: int = quote_count
        self.reply_count: int = reply_count
        self.retweet_count: int = retweet_count
        self.embedded_url: str = self.get_embedded_url()
        self.tweet_url = tweet_url

    def __repr__(self):
        return f"{self.twitter_username} : {self.tweet_id}"

    def get_embedded_url(self):
        url = (
            f"https://publish.twitter.com/oembed?url=https://twitter.com/{self.twitter_username}/status/{self.tweet_id}"
        )
        try:
            return BeautifulSoup(
                urllib.parse.unquote(
                    requests.request(
                        method="GET",
                        url=url,
                        headers=HEADERS,
                    ).json()["html"]
                ).replace("\\", ""),
                "html.parser",
            )
        except KeyError:
            return ""


async def load_user_data(twitter_username, creator_id):
    twitter_user = TwitterUser(twitter_username, creator_id)
    twitter_user.load_twitter_user_data()
    await twitter_user.load_platform_data()


if __name__ == "__main__":
    run_async_function_synchronously(load_user_data, "elonmusk", "2bedf591-5944-4c1d-b586-c56be7b7459f")
