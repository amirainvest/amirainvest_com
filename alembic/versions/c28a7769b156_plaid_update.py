"""plaid update

Revision ID: c28a7769b156
Revises: f19d90e0055d
Create Date: 2022-03-20 03:42:25.199414

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'c28a7769b156'
down_revision = 'f19d90e0055d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bad_plaid_items')
    financial_account_status = postgresql.ENUM('active', 'inactive', 'error', name='financialaccountstatus')
    financial_account_status.create(op.get_bind())
    op.add_column(
        'financial_accounts', sa.Column(
            'status', sa.Enum('active', 'inactive', 'error', server_default='active', name='financialaccountstatus'),
            nullable=True
        )
    )

    op.add_column('financial_accounts', sa.Column('error_message', sa.String(), nullable=True))
    op.alter_column('financial_account_current_holdings', 'latest_price_date',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    op.alter_column('financial_accounts', 'status',
               existing_type=postgresql.ENUM('active', 'inactive', 'error', name='financialaccountstatus'),
               server_default='active',
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('financial_accounts', 'error_message')
    op.drop_column('financial_accounts', 'status')
    op.create_table(
        'bad_plaid_items',
        sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column('plaid_item_id', sa.BIGINT(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['plaid_item_id'], ['plaid_items.id'], name='bad_plaid_items_plaid_item_id_fkey'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='bad_plaid_items_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='bad_plaid_items_pkey'),
        sa.UniqueConstraint('id', name='bad_plaid_items_id_key'),
        sa.UniqueConstraint('plaid_item_id', name='bad_plaid_items_plaid_item_id_key'),
        sa.UniqueConstraint('user_id', 'plaid_item_id', name='bad_plaid_items_user_id_plaid_item_id_key'),
        sa.UniqueConstraint('user_id', name='bad_plaid_items_user_id_key')
    )
    op.alter_column('financial_accounts', 'status',
               existing_type=postgresql.ENUM('active', 'inactive', 'error', name='financialaccountstatus'),
               server_default=None,
               existing_nullable=True)
    op.alter_column('financial_account_current_holdings', 'latest_price_date',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    # ### end Alembic commands ###
