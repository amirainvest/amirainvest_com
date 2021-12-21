from datetime import datetime

import pandas  # type: ignore

from backend.controllers.users import handle_user_create


def load_users_from_csv(csv_filename):
    for _, row in pandas.read_csv(csv_filename).iterrows():
        handle_user_create(
            {
                "sub": "",
                "name": "",
                "bio": "",
                "username": "",
                "picture_url": "",
                "email": "",
                "personal_site_url": "",
                "linkedin_profile": "",
                "email_verified": False,
                "interests_value": False,
                "interests_growth": False,
                "interests_long_term": False,
                "interests_short_term": False,
                "interests_diversification_rating": 0,
                "benchmark": "string",
                "public_profile": False,
                "public_performance": False,
                "public_holdings": False,
                "public_trades": False,
                "is_claimed": False,
                "is_deactivated": False,
                "is_deleted": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "twitter_username": row["twitter_username"],
                "youtube_channel_id": row["youtube_channel_id"],
                "substack_username": row["substack_username"],
            }
        )
