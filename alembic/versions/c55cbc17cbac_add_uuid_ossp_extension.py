"""Add uuid-ossp extension

Revision ID: c55cbc17cbac
Revises:
Create Date: 2022-02-02 05:44:28.502010

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c55cbc17cbac'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE EXTENSION "uuid-ossp";')


def downgrade():
    op.execute('DROP EXTENSION "uuid-ossp";')


