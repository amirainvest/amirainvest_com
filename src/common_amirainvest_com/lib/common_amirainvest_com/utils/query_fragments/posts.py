from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import Query

from common_amirainvest_com.schemas import schema
from common_amirainvest_com.schemas.schema import Bookmarks, Posts, Users, UserSubscriptions
from common_amirainvest_com.utils.generic_utils import get_past_datetime


PAGE_SIZE = 30
MAX_HOURS_AGO = 168  # NUMBER OF HOURS TO QUERY POSTGRES : 168H = 1W
MAX_FEED_SIZE = 200


def all_subscriber_posts(subscriber_id: str, hours_ago):
    return (
        select(Posts)
        .join(UserSubscriptions, UserSubscriptions.creator_id == Posts.creator_id)
        .where(Posts.created_at > get_past_datetime(hours=hours_ago))
        .where(UserSubscriptions.subscriber_id == subscriber_id)
        .order_by(Posts.created_at.desc())
    )


def all_creator_posts(creator_id, hours_ago):
    return (
        select(Posts)
        .where(Posts.creator_id == creator_id)
        .where(Posts.created_at > get_past_datetime(hours=hours_ago))
        .order_by(Posts.created_at.desc())
    )


def all_user_bookmarked_posts(user_id):
    return (
        select(Posts, Bookmarks, Users)
        .join(Bookmarks.post_id == Posts.id)
        .join(Bookmarks.user_id == Users.id)
        .where(Users.id == user_id)
    )


def subscriber_posts(
    subscriber_id: str,
    page_size: int = PAGE_SIZE,
    last_loaded_post_id: int = 0,
    hours_ago: int = MAX_HOURS_AGO,
) -> Query:
    query = (
        select(schema.Posts)
        .join(schema.UserSubscriptions, schema.UserSubscriptions.creator_id == schema.Posts.creator_id)
        .where(schema.UserSubscriptions.subscriber_id == subscriber_id)
    )
    query = latest_posts(query, page_size=page_size, last_loaded_post_id=last_loaded_post_id, hours_ago=hours_ago)
    return query


def latest_posts(
    query: Query,
    page_size: int = PAGE_SIZE,
    last_loaded_post_id: int = 0,
    hours_ago: int = MAX_HOURS_AGO,
) -> Query:
    query = query.where(schema.Posts.created_at > get_past_datetime(hours=hours_ago)).order_by(schema.Posts.id.desc())
    if page_size != -1:
        query = query.limit(page_size)
    if last_loaded_post_id != 0:
        query = query.where(schema.Posts.id < last_loaded_post_id)
    return query


def subscriber_count() -> Query:
    query = select(
        schema.UserSubscriptions.creator_id,
        func.count(schema.UserSubscriptions.creator_id).label("subscriber_count"),
    ).group_by(schema.UserSubscriptions.creator_id)
    return query
