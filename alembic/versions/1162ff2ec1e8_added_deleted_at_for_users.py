"""Added deleted_at for Users

Revision ID: 1162ff2ec1e8
Revises: c6a7ca5b91c3
Create Date: 2022-01-11 01:41:44.701584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1162ff2ec1e8'
down_revision = 'c6a7ca5b91c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'deleted_at')
    # ### end Alembic commands ###
