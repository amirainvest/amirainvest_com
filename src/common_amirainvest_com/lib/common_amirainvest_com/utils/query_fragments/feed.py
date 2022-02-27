import sqlalchemy as sa
from sqlalchemy import and_, func
from sqlalchemy.future import select
from sqlalchemy.sql import Select

from common_amirainvest_com.schemas import schema
from common_amirainvest_com.utils.generic_utils import get_past_datetime
from common_amirainvest_com.utils.sqlalchemy_helpers import DictBundle


PAGE_SIZE = 30
MAX_HOURS_AGO = 168  # NUMBER OF HOURS TO QUERY POSTGRES : 168H = 1W
MAX_FEED_SIZE = 200


def subscriber_posts(
    subscriber_id: str,
    page_size: int = PAGE_SIZE,
    subscriber_feed_last_loaded_post_id: int = 0,
    hours_ago: int = MAX_HOURS_AGO,
) -> Select:
    query = feed_select(subscriber_id=subscriber_id).join(
        schema.UserSubscriptions,
        sa.and_(
            schema.UserSubscriptions.creator_id == schema.Posts.creator_id,
            schema.UserSubscriptions.subscriber_id == subscriber_id,
        ),
    )
    query = latest_posts(
        query,
        page_size=page_size,
        last_loaded_post_id=subscriber_feed_last_loaded_post_id,
        hours_ago=hours_ago,
    )
    return query


def latest_posts(
    query: Select,
    page_size: int = PAGE_SIZE,
    last_loaded_post_id: int = 0,
    hours_ago: int = MAX_HOURS_AGO,
) -> Select:
    query = query.where(schema.Posts.created_at > get_past_datetime(hours=hours_ago)).order_by(schema.Posts.id.desc())
    if page_size != -1:
        query = query.limit(page_size)
    if last_loaded_post_id > 0:
        query = query.where(schema.Posts.id < last_loaded_post_id)
    return query


def subscriber_count() -> Select:
    query = select(
        schema.UserSubscriptions.creator_id,
        func.count(schema.UserSubscriptions.creator_id).label("subscriber_count"),
    ).group_by(schema.UserSubscriptions.creator_id)
    return query


def feed_select(subscriber_id: str) -> Select:
    query = (
        select(
            *[column for column in schema.Posts.__table__.columns],
            # https://docs.sqlalchemy.org/en/20/orm/loading_columns.html#bundles
            DictBundle(
                "creator",
                schema.Users.id.label("id_creator"),
                schema.Users.first_name.label("first_name"),
                schema.Users.last_name.label("last_name"),
                schema.Users.username.label("username"),
                schema.Users.picture_url.label("picture_url"),
                schema.Users.chip_labels.label("chip_labels"),  # type: ignore
            ),
            sa.case(
                [
                    (schema.Bookmarks.post_id.isnot(None), schema.Bookmarks.post_id),
                    (schema.Bookmarks.post_id.is_(None), None),
                ]
            ).label("bookmark_id"),
        )
        .outerjoin(
            schema.Bookmarks,
            and_(
                schema.Bookmarks.post_id == schema.Posts.id,
                schema.Bookmarks.user_id == subscriber_id,
                schema.Bookmarks.is_deleted.isnot(True),
            ),
        )
        .join(
            schema.Users,
            schema.Users.id == schema.Posts.creator_id,
        )
    )
    return query
