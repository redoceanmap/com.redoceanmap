"""create role_tabs and seed basic grade

등급별 상단 탭 게이팅 — 역할별 노출 탭(role_tabs) + 기본 등급(basic) 시드.
admin·basic 두 역할에 탭 5종 전부를 시드하고, 기존 미탈퇴 유저 전원에 basic을
백필한다(신규 가입은 인터랙터가 자동 부여). 시드는 전부 멱등(ON CONFLICT).

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TAB_KEYS = ("history", "market", "stock", "vision", "automation")


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'role_tabs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id'), nullable=False),
        sa.Column('tab_key', sa.String(length=50), nullable=False),
        sa.UniqueConstraint('role_id', 'tab_key'),
    )
    op.create_index(op.f('ix_role_tabs_role_id'), 'role_tabs', ['role_id'])

    op.execute(
        sa.text(
            "INSERT INTO roles (code, name) VALUES ('basic', '기본') "
            "ON CONFLICT (code) DO NOTHING"
        )
    )
    values = ", ".join(f"('{k}')" for k in TAB_KEYS)
    op.execute(
        sa.text(
            "INSERT INTO role_tabs (role_id, tab_key) "
            f"SELECT r.id, t.key FROM roles r CROSS JOIN (VALUES {values}) AS t(key) "
            "WHERE r.code IN ('admin', 'basic') "
            "ON CONFLICT (role_id, tab_key) DO NOTHING"
        )
    )
    # 백필 — 탈퇴자는 제외(withdraw가 역할 전량 회수를 불변식으로 삼는다).
    op.execute(
        sa.text(
            "INSERT INTO user_roles (user_id, role_id) "
            "SELECT u.id, r.id FROM users u, roles r "
            "WHERE r.code = 'basic' AND u.deleted_at IS NULL "
            "ON CONFLICT (user_id, role_id) DO NOTHING"
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('role_tabs')
    op.execute(
        sa.text(
            "DELETE FROM user_roles WHERE role_id = (SELECT id FROM roles WHERE code = 'basic')"
        )
    )
    op.execute(sa.text("DELETE FROM roles WHERE code = 'basic'"))
