"""init 2

Revision ID: 98b0e5f358c5
Revises: e1c21f8d6359
Create Date: 2021-12-20 16:45:10.359135

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "98b0e5f358c5"
down_revision = "e1c21f8d6359"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "bookmarks", ["id"])
    op.create_unique_constraint(None, "broadcast_requests", ["id"])
    op.create_unique_constraint(None, "financial_account_current_holdings", ["id"])
    op.create_unique_constraint(None, "financial_account_transactions", ["id"])
    op.create_unique_constraint(None, "financial_accounts", ["id"])
    op.create_unique_constraint(None, "financial_institutions", ["id"])
    op.create_unique_constraint(None, "husk_requests", ["id"])
    op.create_unique_constraint(None, "post_comments", ["id"])
    op.create_unique_constraint(None, "post_reads", ["id"])
    op.create_unique_constraint(None, "posts", ["id"])
    op.create_unique_constraint(None, "securities", ["id"])
    op.create_unique_constraint(None, "security_prices", ["id"])
    op.create_unique_constraint(None, "substack_articles", ["article_id"])
    op.create_unique_constraint(None, "substack_users", ["username"])
    op.create_unique_constraint(None, "tweet_annotations", ["id"])
    op.create_unique_constraint(None, "tweet_cashtags", ["id"])
    op.create_unique_constraint(None, "tweet_hashtags", ["id"])
    op.create_unique_constraint(None, "tweet_mentions", ["id"])
    op.create_unique_constraint(None, "tweet_urls", ["id"])
    op.create_unique_constraint(None, "tweets", ["tweet_id"])
    op.create_unique_constraint(None, "twitter_users", ["twitter_user_id"])
    op.create_unique_constraint(None, "user_media_errors", ["id"])
    op.create_unique_constraint(None, "user_subscriptions", ["id"])
    op.create_unique_constraint(None, "users", ["id"])
    op.create_unique_constraint(None, "youtube_videos", ["video_id"])
    op.create_unique_constraint(None, "youtubers", ["channel_id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "youtubers", type_="unique")
    op.drop_constraint(None, "youtube_videos", type_="unique")
    op.drop_constraint(None, "users", type_="unique")
    op.drop_constraint(None, "user_subscriptions", type_="unique")
    op.drop_constraint(None, "user_media_errors", type_="unique")
    op.drop_constraint(None, "twitter_users", type_="unique")
    op.drop_constraint(None, "tweets", type_="unique")
    op.drop_constraint(None, "tweet_urls", type_="unique")
    op.drop_constraint(None, "tweet_mentions", type_="unique")
    op.drop_constraint(None, "tweet_hashtags", type_="unique")
    op.drop_constraint(None, "tweet_cashtags", type_="unique")
    op.drop_constraint(None, "tweet_annotations", type_="unique")
    op.drop_constraint(None, "substack_users", type_="unique")
    op.drop_constraint(None, "substack_articles", type_="unique")
    op.drop_constraint(None, "security_prices", type_="unique")
    op.drop_constraint(None, "securities", type_="unique")
    op.drop_constraint(None, "posts", type_="unique")
    op.drop_constraint(None, "post_reads", type_="unique")
    op.drop_constraint(None, "post_comments", type_="unique")
    op.drop_constraint(None, "husk_requests", type_="unique")
    op.drop_constraint(None, "financial_institutions", type_="unique")
    op.drop_constraint(None, "financial_accounts", type_="unique")
    op.drop_constraint(None, "financial_account_transactions", type_="unique")
    op.drop_constraint(None, "financial_account_current_holdings", type_="unique")
    op.drop_constraint(None, "broadcast_requests", type_="unique")
    op.drop_constraint(None, "bookmarks", type_="unique")
    # ### end Alembic commands ###
