"""catchup

Revision ID: 15b1b78d1952
Revises: cb1233dae73c
Create Date: 2022-01-28 19:49:49.316998

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15b1b78d1952'
down_revision = 'cb1233dae73c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'benchmarks', ['id'])
    op.create_unique_constraint(None, 'chip_labels', ['id'])
    op.create_unique_constraint(None, 'trading_strategies', ['id'])
    op.create_unique_constraint(None, 'user_feedback', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_feedback', type_='unique')
    op.drop_constraint(None, 'trading_strategies', type_='unique')
    op.drop_constraint(None, 'chip_labels', type_='unique')
    op.drop_constraint(None, 'benchmarks', type_='unique')
    # ### end Alembic commands ###
