from sqlalchemy.future import select

from common_amirainvest_com.schemas.schema import Bookmarks, Posts, Users, UserSubscriptions
from common_amirainvest_com.utils.generic_utils import get_past_datetime


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
