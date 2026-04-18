"""add companies approvals activity_logs agent_secrets task_comments manager_id budget fields

Revision ID: dc3e58e1014d
Revises: f8002900fbaf
Create Date: 2026-04-18 13:10:43.447809

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'dc3e58e1014d'
down_revision = 'f8002900fbaf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('goal', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.String(), nullable=False),
        sa.Column('monthly_budget', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('budget_spent', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('companies_owner_id_fkey')),
        sa.PrimaryKeyConstraint('id', name=op.f('companies_pkey')),
        sa.UniqueConstraint('company_id', name=op.f('companies_company_id_key'))
    )
    op.create_index(op.f('ix_companies_company_id'), 'companies', ['company_id'], unique=True)

    # Add company_id and manager_id to agents
    op.add_column('agents', sa.Column('manager_id', sa.String(), nullable=True))
    op.add_column('agents', sa.Column('company_id', sa.String(), nullable=True))
    op.add_column('agents', sa.Column('monthly_budget', sa.Numeric(precision=18, scale=2), nullable=True))
    op.add_column('agents', sa.Column('budget_spent', sa.Numeric(precision=18, scale=2), nullable=True))
    op.add_column('agents', sa.Column('llm_tokens_used', sa.Integer(), nullable=True))
    op.add_column('agents', sa.Column('llm_cost_usd', sa.Numeric(precision=18, scale=4), nullable=True))
    op.create_foreign_key(op.f('agents_manager_id_fkey'), 'agents', 'agents', ['manager_id'], ['id'])
    op.create_foreign_key(op.f('agents_company_id_fkey'), 'agents', 'companies', ['company_id'], ['id'])

    # Create approvals table
    op.create_table(
        'approvals',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('approval_id', sa.String(length=255), nullable=False),
        sa.Column('company_id', sa.String(), nullable=True),
        sa.Column('approval_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('payload', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('requested_by_agent_id', sa.String(), nullable=True),
        sa.Column('approved_by_user_id', sa.String(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['approved_by_user_id'], ['users.id'], name=op.f('approvals_approved_by_user_id_fkey')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name=op.f('approvals_company_id_fkey')),
        sa.ForeignKeyConstraint(['requested_by_agent_id'], ['agents.id'], name=op.f('approvals_requested_by_agent_id_fkey')),
        sa.PrimaryKeyConstraint('id', name=op.f('approvals_pkey')),
        sa.UniqueConstraint('approval_id', name=op.f('approvals_approval_id_key'))
    )
    op.create_index(op.f('ix_approvals_approval_id'), 'approvals', ['approval_id'], unique=True)

    # Create activity_logs table
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=True),
        sa.Column('actor_type', sa.String(length=50), nullable=False),
        sa.Column('actor_id', sa.String(), nullable=False),
        sa.Column('actor_name', sa.String(length=255), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_description', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name=op.f('activity_logs_company_id_fkey')),
        sa.PrimaryKeyConstraint('id', name=op.f('activity_logs_pkey'))
    )

    # Create agent_secrets table
    op.create_table(
        'agent_secrets',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('key_name', sa.String(length=100), nullable=False),
        sa.Column('encrypted_value', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], name=op.f('agent_secrets_agent_id_fkey'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('agent_secrets_pkey'))
    )

    # Create task_comments table
    op.create_table(
        'task_comments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('task_id', sa.String(), nullable=False),
        sa.Column('author_type', sa.String(length=50), nullable=False),
        sa.Column('author_id', sa.String(), nullable=False),
        sa.Column('author_name', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.task_id'], name=op.f('task_comments_task_id_fkey'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('task_comments_pkey'))
    )


def downgrade() -> None:
    op.drop_table('task_comments')
    op.drop_table('agent_secrets')
    op.drop_table('activity_logs')
    op.drop_index(op.f('ix_approvals_approval_id'), table_name='approvals')
    op.drop_table('approvals')
    op.drop_constraint(op.f('agents_company_id_fkey'), 'agents', type_='foreignkey')
    op.drop_constraint(op.f('agents_manager_id_fkey'), 'agents', type_='foreignkey')
    op.drop_column('agents', 'llm_cost_usd')
    op.drop_column('agents', 'llm_tokens_used')
    op.drop_column('agents', 'budget_spent')
    op.drop_column('agents', 'monthly_budget')
    op.drop_column('agents', 'company_id')
    op.drop_column('agents', 'manager_id')
    op.drop_index(op.f('ix_companies_company_id'), table_name='companies')
    op.drop_table('companies')
