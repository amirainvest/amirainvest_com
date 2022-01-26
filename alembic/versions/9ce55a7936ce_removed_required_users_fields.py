"""Removed required Users fields

Revision ID: 9ce55a7936ce
Revises: cedb27a639c0
Create Date: 2022-01-17 20:19:50.621864

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ce55a7936ce'
down_revision = 'e8e86510e598'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'picture_url',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.create_unique_constraint("users_email_uc", 'users', ['email'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("users_email_uc", 'users', type_='unique')
    op.alter_column('users', 'picture_url',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
