import time

import feedparser
from bs4 import BeautifulSoup

from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from common_amirainvest_com.utils.datetime_utils import parse_iso_8601_from_string
from common_amirainvest_com.utils.logger import log
from data_imports_amirainvest_com.controllers import posts
from data_imports_amirainvest_com.controllers.substack_articles import (
    create_substack_article,
    get_substack_articles_for_username,
)
from data_imports_amirainvest_com.controllers.substack_users import create_substack_user
from data_imports_amirainvest_com.controllers.users import get_user
from data_imports_amirainvest_com.platforms.platforms import PlatformUser


class SubstackUser(PlatformUser):
    def __init__(self, username, creator_id):
        super().__init__()
        self.username = username
        self.user_url = f"https://{self.username}.substack.com/feed"
        self.creator_id = creator_id
        self.is_deleted = False

    def get_unique_id(self):
        return self.username

    async def get_articles_from_url(self):
        articles = []
        article_posts = []
        existing_articles = await get_substack_articles_for_username(self.username)
        user = await get_user(self.creator_id)
        for article in feedparser.parse(self.user_url).entries:
            if article["id"] not in [x.article_id for x in existing_articles]:
                summary = BeautifulSoup(article["summary"], features="html.parser").get_text()
                created_at = parse_iso_8601_from_string(time.strftime("%Y-%m-%d %H:%M:%S", article["published_parsed"]))
                articles.append(
                    {
                        "summary": summary,
                        "title": article["title"],
                        "created_at": created_at,
                        "url": article["link"],
                        "article_id": article["id"],
                        "author": article.get("author"),
                        "username": self.username,
                    }
                )
                article_posts.append(
                    {
                        "creator_id": self.creator_id,
                        "platform": "substack",
                        "platform_user_id": self.username,
                        "platform_post_id": article["id"],
                        "profile_img_url": "",
                        "text": summary,
                        "html": "",
                        "title": article["title"],
                        "profile_url": "",
                        "chip_labels": user.chip_labels,
                        "created_at": created_at,
                        "updated_at": created_at,
                    }
                )
        return articles, article_posts

    async def load_platform_data(self):
        new_articles, article_posts = await self.get_articles_from_url()
        substack_user_exists = await self.get_user_platform_pair_exists("substack", self.get_unique_id())
        if not substack_user_exists:
            log.info(f"Added new Substack user: {self.username}")
            await create_substack_user(self.__dict__)
        for article in new_articles:
            log.info(f"New article found for Substack: {article['title']}")
            await create_substack_article(article)
        for article_post in article_posts:
            await posts.create_post(article_post)
            posts.put_post_on_creators_redis_feeds(article_post)
            await posts.put_post_on_subscriber_redis_feeds(article_post)


async def load_user_data(username, creator_id):
    substack_user = SubstackUser(username, creator_id)
    await substack_user.load_platform_data()


from sqlalchemy import insert

from common_amirainvest_com.schemas.schema import Users
from common_amirainvest_com.utils.decorators import Session


@Session
async def create_user(session):
    await session.execute(insert(Users).values({"sub": "", "name": "", "username": "", "email": ""}))


if __name__ == "__main__":
    # run_async_function_synchronously(create_user)
    run_async_function_synchronously(load_user_data, "saeedjones", "1a243f2c-53fd-41ad-a049-92fd732fe169")
