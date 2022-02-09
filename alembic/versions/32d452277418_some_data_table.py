"""some data table

Revision ID: 32d452277418
Revises: f752a6542a12
Create Date: 2022-02-09 15:36:04.142216

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32d452277418'
down_revision = 'f752a6542a12'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('market_holidays',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('holiday_date', sa.DateTime(), nullable=False),
    sa.Column('settlement_date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('holiday_date'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('market_holidays')
    # ### end Alembic commands ###
