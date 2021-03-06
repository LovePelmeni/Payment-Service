"""Migrations

Revision ID: 64ea0047fd63
Revises: 
Create Date: 2022-06-03 22:22:54.661439

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64ea0047fd63'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('customers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('stripe_customer_id', sa.String(length=100), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('stripe_customer_id')
    )
    op.create_table('subscriptions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.String(length=100), nullable=True),
    sa.Column('subscription_name', sa.String(length=100), nullable=False),
    sa.Column('price_id', sa.String(length=100), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('currency', sa.String(length=10), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('payment_intent_id', sa.String(length=100), nullable=False),
    sa.Column('charge_id', sa.String(length=100), nullable=False),
    sa.Column('subscription', sa.Integer(), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('purchaser', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['purchaser'], ['customers.id'], name='fk_payments_customers_id_purchaser'),
    sa.ForeignKeyConstraint(['subscription'], ['subscriptions.id'], name='fk_payments_subscriptions_id_subscription'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('refunds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('refund_id', sa.String(length=100), nullable=False),
    sa.Column('payment_id', sa.Integer(), nullable=True),
    sa.Column('purchaser', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['purchaser'], ['customers.id'], name='fk_refunds_customers_id_purchaser'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('refunds')
    op.drop_table('payments')
    op.drop_table('subscriptions')
    op.drop_table('customers')
    # ### end Alembic commands ###
