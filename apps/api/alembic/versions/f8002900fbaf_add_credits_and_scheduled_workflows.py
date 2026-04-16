"""add credits and scheduled workflows

Revision ID: f8002900fbaf
Revises: a294f2ad5a3b
Create Date: 2026-04-16 16:05:56.121415

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f8002900fbaf'
down_revision = 'a294f2ad5a3b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add credit columns to users
    op.add_column('users', sa.Column('credits_balance', sa.Numeric(precision=18, scale=4), nullable=True))
    op.add_column('users', sa.Column('credits_spent', sa.Numeric(precision=18, scale=4), nullable=True))
    op.add_column('users', sa.Column('subscription_tier', sa.String(length=50), nullable=True))
    
    # Set defaults for existing rows
    op.execute("UPDATE users SET credits_balance = 500, credits_spent = 0, subscription_tier = 'free'")
    
    # Make columns non-nullable after setting defaults
    op.alter_column('users', 'credits_balance', nullable=False)
    op.alter_column('users', 'credits_spent', nullable=False)
    op.alter_column('users', 'subscription_tier', nullable=False)
    
    # Create scheduled_workflows table
    op.create_table(
        'scheduled_workflows',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('schedule_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('schedule', sa.String(length=100), nullable=False),
        sa.Column('pipeline_type', sa.String(length=100), nullable=False),
        sa.Column('context', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('owner_id', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('run_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.UniqueConstraint('schedule_id')
    )


def downgrade() -> None:
    op.drop_table('scheduled_workflows')
    op.drop_column('users', 'subscription_tier')
    op.drop_column('users', 'credits_spent')
    op.drop_column('users', 'credits_balance')
