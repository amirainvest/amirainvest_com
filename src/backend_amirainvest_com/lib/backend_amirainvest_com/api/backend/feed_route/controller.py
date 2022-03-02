from operator import or_

# from tracemalloc import stop
from typing import List, Tuple

import sqlalchemy
import sqlalchemy as sa
from sqlalchemy import Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import text

import common_amirainvest_com.utils.query_fragments.feed as qf
from backend_amirainvest_com.api.backend.feed_route.model import FeedType, GetResponseModel, ListInputModel
from common_amirainvest_com.schemas import schema
from common_amirainvest_com.utils.decorators import Session


async def list_controller(
    feed_info: ListInputModel,
    subscriber_id: str,
    page_size: int = qf.PAGE_SIZE,
) -> Tuple[List[GetResponseModel], FeedType]:
    wanted_feed_type = feed_info.feed_type

    return_feed = []
    return_feed_type = wanted_feed_type

    if wanted_feed_type == FeedType.creator:
        return_feed = await get_creator_feed(
            feed_info=feed_info,
            subscriber_id=subscriber_id,
            page_size=page_size,
        )
    elif wanted_feed_type == FeedType.subscriber:
        return_feed = await get_subscriber_feed(
            feed_info=feed_info,
            subscriber_id=subscriber_id,
            page_size=page_size,
        )

    if return_feed == []:
        return_feed = await get_discovery_feed(
            feed_info=feed_info,
            subscriber_id=subscriber_id,
            page_size=page_size,
        )
        return_feed_type = FeedType.discovery
    return return_feed, return_feed_type


@Session
async def get_subscriber_feed(
    session: AsyncSession,
    feed_info: ListInputModel,
    subscriber_id: str,
    page_size: int = qf.PAGE_SIZE,
    hours_ago: int = qf.MAX_HOURS_AGO,
) -> List[GetResponseModel]:
    query = qf.subscriber_posts(
        subscriber_id=subscriber_id,
        page_size=page_size,
        subscriber_feed_last_loaded_date=feed_info.subscriber_feed_last_loaded_date,
        hours_ago=hours_ago,
    )


    data = await session.execute(query)
    posts = [GetResponseModel.from_orm(post) for post in data]
    return posts


@Session
async def get_creator_feed(
    session: AsyncSession,
    feed_info: ListInputModel,
    subscriber_id: str,
    page_size: int = qf.PAGE_SIZE,
    hours_ago: int = -1,
) -> List[GetResponseModel]:
    query = qf.feed_select(subscriber_id=subscriber_id).where(schema.Posts.creator_id == feed_info.creator_id)
    

    query = qf.latest_posts(
        query,
        page_size=page_size,
        last_loaded_date=feed_info.creator_feed_last_loaded_date,
        hours_ago=hours_ago,
    )


    data = await session.execute(query)
    posts = [GetResponseModel.from_orm(post) for post in data]
    return posts
    

@Session
async def get_discovery_feed(
    session: AsyncSession,
    feed_info: ListInputModel,
    subscriber_id: str,
    page_size: int = qf.PAGE_SIZE,
    hours_ago: int = qf.MAX_HOURS_AGO,
) -> List[GetResponseModel]:
    subscriber_posts_cte = qf.subscriber_posts(
        subscriber_id=subscriber_id,
        page_size=-1,
        subscriber_feed_last_loaded_date=feed_info.subscriber_feed_last_loaded_date,
        hours_ago=hours_ago,
    ).cte()
    subscriber_count_cte = qf.subscriber_count().cte()

    query = (
        qf.feed_select(subscriber_id=subscriber_id)
        .outerjoin(
            subscriber_posts_cte,
            subscriber_posts_cte.c.id == schema.Posts.id,
        )
        .filter(subscriber_posts_cte.c.id.is_(None))
        .outerjoin(
            subscriber_count_cte,
            subscriber_count_cte.c.creator_id == schema.Posts.creator_id,
        )
    )

    if feed_info.discovery_feed_last_loaded_date is not None:
        query = query.where(schema.Posts.created_at < feed_info.discovery_feed_last_loaded_date)

    # TODO: Need to add in logic for when a ticker is at the beginning of the text or
    #       if there is a punctuation after it.

    if feed_info.company_ticker is not None:
        # This should probably be a table, not a text file.. but I don't really know
        # how to create a new table in our dev framework and this was faster.
        f = open("/opt/english_stopwords.txt", "r")
        stopwords = f.read()

        # Checks to see if a ticker entered exists in our securities table. If it doesn't assume
        # the ticker is invalid and return null (I would return an error, but I'm unsure
        # how to return errors)
        try:
            company_name = (
                await session.execute(
                    text(
                        f"SELECT name FROM securities WHERE securities.ticker_symbol = \
                        '{feed_info.company_ticker.upper()}'"
                    )
                )
            ).one()[0]
        except NoResultFound:
            return []

        # Logic here is that if a company's ticker is is also a commonly found english stop word, we should only
        # search on the company name and the ticker with the cashtag symbol
        # in front of it. Example of it being an issue, "BE" or "U". Both can commonly appear and not be references
        # to tickers. Where as if you see UPST without a cashtag
        # its still most likely that the person is talking about the company Upstart.
        # This is imperfect, but I think will do a decent enough job for the time being.
        if feed_info.company_ticker.lower() in stopwords:
            query = query.filter(
                or_(
                    or_(
                        or_(
                            schema.Posts.content.ilike(f"%>${feed_info.company_ticker}<%"),
                            schema.Posts.title.ilike(f"% ${feed_info.company_ticker} %"),
                        ),
                        schema.Posts.content.ilike(f"% ${feed_info.company_ticker} %"),
                    ),
                    or_(schema.Posts.content.ilike(f"%{company_name}%"), schema.Posts.title.ilike(f"%{company_name}%")),
                )
            )

        else:
            query = query.filter(
                or_(
                    or_(
                        or_(
                            schema.Posts.content.ilike(f"%>${feed_info.company_ticker}<%"),
                            schema.Posts.title.ilike(f"% ${feed_info.company_ticker} %"),
                        ),
                        schema.Posts.content.ilike(f"% ${feed_info.company_ticker} %"),
                    ),
                    or_(
                        or_(
                            schema.Posts.content.ilike(f"% {feed_info.company_ticker} %"),
                            schema.Posts.title.ilike(f"% {feed_info.company_ticker} %"),
                        ),
                        or_(
                            schema.Posts.content.ilike(f"%{company_name}%"),
                            schema.Posts.title.ilike(f"%{company_name}%"),
                        ),
                    ),
                )
            )

    query = (
        query.order_by(sa.cast(schema.Posts.created_at, Date).desc())
        .order_by(schema.Posts.platform.asc())
        .order_by(sa.sql.extract("hour", schema.Posts.created_at).desc())
        .order_by(subscriber_count_cte.c.subscriber_count.desc())
    )

    query = query.limit(page_size)

    data = (await session.execute(query)).all()
    posts = [GetResponseModel.from_orm(post) for post in data]
    return posts
