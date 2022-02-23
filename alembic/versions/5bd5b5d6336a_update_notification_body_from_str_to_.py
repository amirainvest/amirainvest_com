"""update notification body from str to jsonb

Revision ID: 5bd5b5d6336a
Revises: a65d664c3658
Create Date: 2022-02-21 18:50:52.582852

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5bd5b5d6336a'
down_revision = 'a65d664c3658'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(None, 'market_holidays', ['id'])
    op.create_unique_constraint(None, 'security_information', ['id'])

    op.drop_column('notifications', 'body')
    op.add_column('notifications', sa.Column('body', postgresql.JSONB(astext_type=sa.Text()), nullable=False))


def downgrade():
    op.drop_constraint(None, 'security_information', type_='unique')
    op.drop_constraint(None, 'market_holidays', type_='unique')
    op.drop_column('notifications', 'body')
    op.add_column('notifications', sa.Column('body', sa.String(), nullable=False))
