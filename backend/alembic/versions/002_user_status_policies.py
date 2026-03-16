"""Add user status and policy tables

Revision ID: 002_user_status_policies
Revises: 001_initial_schema
Create Date: 2026-03-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002_user_status_policies'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add status column to users table
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'ADMIN'")
    op.execute("CREATE TYPE userstatus AS ENUM ('PENDING', 'APPROVED', 'REJECTED')")
    
    op.add_column('users', sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='userstatus'), nullable=False, server_default='PENDING'))
    op.add_column('users', sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('approved_by', sa.Integer(), nullable=True))
    
    # Create policies table
    op.create_table('policies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('policy_type', sa.Enum('LOGICAL', 'NATURAL_LANGUAGE', name='policytype'), nullable=False),
        sa.Column('natural_language', sa.Text(), nullable=True),
        sa.Column('dsl', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'DRAFT', name='policystatus'), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index(op.f('ix_policies_status'), 'policies', ['status'], unique=False)
    op.create_index(op.f('ix_policies_priority'), 'policies', ['priority'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_policies_priority'), table_name='policies')
    op.drop_index(op.f('ix_policies_status'), table_name='policies')
    op.drop_table('policies')
    
    op.drop_column('users', 'approved_by')
    op.drop_column('users', 'approved_at')
    op.drop_column('users', 'status')
    
    op.execute('DROP TYPE IF EXISTS userstatus')
    op.execute('DROP TYPE IF EXISTS policytype')
    op.execute('DROP TYPE IF EXISTS policystatus')
