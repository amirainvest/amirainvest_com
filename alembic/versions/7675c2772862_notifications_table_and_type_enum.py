"""notifications table and type enum

Revision ID: 7675c2772862
Revises: 4f2d7e9d45b9
Create Date: 2022-01-22 18:46:30.803617

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7675c2772862'
down_revision = '4f2d7e9d45b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notifications',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('notification_type', sa.Enum('trade', 'creator_join', 'amira_post', name='notificationtypes'), nullable=False),
    sa.Column('text', sa.String(), nullable=True),
    sa.Column('redirect_id', sa.String(), nullable=True),
    sa.Column('mark_as_read', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notifications')
    # ### end Alembic commands ###
