"""Change notifications body type

Revision ID: accc23c40cda
Revises: a65d664c3658
Create Date: 2022-02-20 02:15:58.017310

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'accc23c40cda'
down_revision = 'a65d664c3658'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(None, 'market_holidays', ['id'])
    op.create_unique_constraint(None, 'security_information', ['id'])

    op.drop_column('notifications', 'body')
    op.add_column('notifications', sa.Column('body', sa.JSON(), nullable=False))


def downgrade():
    op.drop_constraint(None, 'security_information', type_='unique')
    op.drop_constraint(None, 'market_holidays', type_='unique')

    op.drop_column('notifications', 'body')
    op.add_column('notifications', sa.Column('body', sa.String(), nullable=False))
