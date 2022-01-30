"""added app config table

Revision ID: cb1233dae73c
Revises: 4f2d7e9d45b9
Create Date: 2022-01-22 20:05:44.262868

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "cb1233dae73c"
down_revision = "17326bbd2fee"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "benchmarks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "chip_labels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "trading_strategies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.add_column("users", sa.Column("trading_strategies", sa.ARRAY(sa.String()), nullable=True))
    op.drop_column("users", "interests_long_term")
    op.drop_column("users", "interests_short_term")
    op.drop_column("users", "interests_growth")
    op.drop_column("users", "interests_value")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("interests_value", sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column("users", sa.Column("interests_growth", sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column("users", sa.Column("interests_short_term", sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column("users", sa.Column("interests_long_term", sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column("users", "trading_strategies")
    op.drop_table("trading_strategies")
    op.drop_table("chip_labels")
    op.drop_table("benchmarks")
    # ### end Alembic commands ###
