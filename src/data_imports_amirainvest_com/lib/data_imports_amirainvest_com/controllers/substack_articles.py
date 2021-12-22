from sqlalchemy import select

from common_amirainvest_com.schemas.schema import SubstackArticles
from common_amirainvest_com.utils.decorators import Session


def all_substack_user_articles(username):
    return select(SubstackArticles).where(SubstackArticles.username == username)


@Session
async def create_substack_article(session, substack_article_data: dict):
    substack_article = SubstackArticles(**substack_article_data)
    session.add(substack_article)
    return substack_article


@Session
async def get_most_recent_substack_article_for_user(session, username):
    article = await session.execute(
        all_substack_user_articles(username).order_by(SubstackArticles.created_at.desc()).limit(1)
    )
    return article.scalars().one()


@Session
async def get_substack_articles_for_username(session, username: str):
    articles = await session.execute(all_substack_user_articles(username))
    return articles.scalars().all()
