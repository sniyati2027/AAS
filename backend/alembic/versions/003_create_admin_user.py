"""Create initial admin user

Revision ID: 003_create_admin_user
Revises: 002_user_status_policies
Create Date: 2026-03-15

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

revision = '003_create_admin_user'
down_revision = '002_user_status_policies'
branch_labels = None
depends_on = None


def upgrade():
    # Create initial admin user (password: admin123)
    # Use bcrypt hash for password "admin123"
    op.execute("""
        INSERT INTO users (email, hashed_password, role, status, is_active, created_at)
        VALUES (
            'admin@atlasuniversity.edu.in',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS8lhCHSm',
            'ADMIN',
            'APPROVED',
            true,
            NOW()
        )
        ON CONFLICT (email) DO NOTHING;
    """)


def downgrade():
    op.execute("""
        DELETE FROM users WHERE email = 'admin@atlasuniversity.edu.in';
    """)
