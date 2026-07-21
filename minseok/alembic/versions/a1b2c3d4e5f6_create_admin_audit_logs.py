"""create admin audit logs

어드민 감사 로그 테이블 + audit:read 권한 시드(admin 역할 매핑).
관리자 행위(역할 부여/회수)의 영속 기록 — 대중적 어드민의 표준 기능.

Revision ID: a1b2c3d4e5f6
Revises: f0a1b2c3d4e5
Create Date: 2026-07-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f0a1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'admin_audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('actor_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('detail', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f('ix_admin_audit_logs_actor_id'), 'admin_audit_logs', ['actor_id'])
    op.create_index(op.f('ix_admin_audit_logs_action'), 'admin_audit_logs', ['action'])

    # audit:read 권한 시드 + admin 역할 매핑 (멱등 — 재실행 대비 존재 검사)
    op.execute(sa.text(
        "INSERT INTO permissions (code, description) "
        "SELECT 'audit:read', '어드민 감사 로그 조회' "
        "WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE code = 'audit:read')"
    ))
    op.execute(sa.text(
        "INSERT INTO role_permissions (role_id, permission_id) "
        "SELECT r.id, p.id FROM roles r, permissions p "
        "WHERE r.code = 'admin' AND p.code = 'audit:read' "
        "AND NOT EXISTS (SELECT 1 FROM role_permissions rp WHERE rp.role_id = r.id AND rp.permission_id = p.id)"
    ))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(sa.text(
        "DELETE FROM role_permissions WHERE permission_id = "
        "(SELECT id FROM permissions WHERE code = 'audit:read')"
    ))
    op.execute(sa.text("DELETE FROM permissions WHERE code = 'audit:read'"))
    op.drop_table('admin_audit_logs')
