"""create rbac tables

정식 RBAC 4테이블 + 정적 시드(admin 역할 · 어드민 권한 6종 · 매핑).
user_roles는 환경별 데이터라 시드하지 않는다 — 최초 부여는 scripts/grant_admin.py.

Revision ID: f0a1b2c3d4e5
Revises: e7f8a9b0c1d2
Create Date: 2026-07-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0a1b2c3d4e5'
down_revision: Union[str, Sequence[str], None] = 'e7f8a9b0c1d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PERMISSIONS = [
    ("dashboard:read", "어드민 대시보드 KPI 조회"),
    ("areas:read", "어드민 상권 목록 조회"),
    ("members:read", "어드민 회원·역할 구성 조회"),
    ("members:write", "어드민 회원 역할 부여/회수"),
    ("recommendations:read", "어드민 추천 기록 조회"),
    ("datasources:read", "어드민 데이터셋 현황 조회"),
]


def upgrade() -> None:
    """Upgrade schema."""
    roles = op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.UniqueConstraint('code'),
    )
    op.create_index(op.f('ix_roles_code'), 'roles', ['code'])
    permissions = op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.UniqueConstraint('code'),
    )
    op.create_index(op.f('ix_permissions_code'), 'permissions', ['code'])
    op.create_table(
        'user_roles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id'), nullable=False),
        sa.UniqueConstraint('user_id', 'role_id'),
    )
    op.create_index(op.f('ix_user_roles_user_id'), 'user_roles', ['user_id'])
    op.create_index(op.f('ix_user_roles_role_id'), 'user_roles', ['role_id'])
    op.create_table(
        'role_permissions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id'), nullable=False),
        sa.Column('permission_id', sa.Integer(), sa.ForeignKey('permissions.id'), nullable=False),
        sa.UniqueConstraint('role_id', 'permission_id'),
    )
    op.create_index(op.f('ix_role_permissions_role_id'), 'role_permissions', ['role_id'])
    op.create_index(op.f('ix_role_permissions_permission_id'), 'role_permissions', ['permission_id'])

    # 정적 시드 — admin 역할이 어드민 권한 6종 전부를 갖는다.
    op.bulk_insert(roles, [{"id": 1, "code": "admin", "name": "관리자"}])
    op.bulk_insert(
        permissions,
        [{"id": i, "code": code, "description": desc} for i, (code, desc) in enumerate(PERMISSIONS, start=1)],
    )
    op.execute(
        sa.text(
            "INSERT INTO role_permissions (role_id, permission_id) "
            "SELECT 1, id FROM permissions"
        )
    )
    # bulk_insert가 id를 명시 삽입했으므로 시퀀스를 맞춘다(이후 INSERT 충돌 방지).
    op.execute(sa.text("SELECT setval(pg_get_serial_sequence('roles', 'id'), (SELECT max(id) FROM roles))"))
    op.execute(
        sa.text("SELECT setval(pg_get_serial_sequence('permissions', 'id'), (SELECT max(id) FROM permissions))")
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('role_permissions')
    op.drop_table('user_roles')
    op.drop_table('permissions')
    op.drop_table('roles')
