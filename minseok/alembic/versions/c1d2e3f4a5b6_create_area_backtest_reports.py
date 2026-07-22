"""상권 점수 워크포워드 백테스트 리포트 + analytics:read 권한 시드.

scripts/backtest_area_score.py가 실행당 1행(집계 payload JSONB)을 적재하고,
어드민(/admin/market-backtest·/admin/forecasts)은 analytics:read 권한으로 조회한다.
행 스키마를 고정하지 않는 이유: 산출물이 "집계 리포트 문서" 1건이라 정규화 이득이 없다.

Revision ID: c1d2e3f4a5b6
Revises: b0c1d2e3f4a5
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'b0c1d2e3f4a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'area_score_backtest_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ran_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('params', postgresql.JSONB(), nullable=False),
        sa.Column('payload', postgresql.JSONB(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # analytics:read 권한 시드 + admin 역할 매핑 (멱등 — a1b2c3d4e5f6 패턴)
    op.execute(sa.text(
        "INSERT INTO permissions (code, description) "
        "SELECT 'analytics:read', '어드민 분석 검증 데이터 조회(예측 채점·상권 백테스트)' "
        "WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE code = 'analytics:read')"
    ))
    op.execute(sa.text(
        "INSERT INTO role_permissions (role_id, permission_id) "
        "SELECT r.id, p.id FROM roles r, permissions p "
        "WHERE r.code = 'admin' AND p.code = 'analytics:read' "
        "AND NOT EXISTS (SELECT 1 FROM role_permissions rp WHERE rp.role_id = r.id AND rp.permission_id = p.id)"
    ))


def downgrade() -> None:
    op.execute(sa.text(
        "DELETE FROM role_permissions WHERE permission_id = "
        "(SELECT id FROM permissions WHERE code = 'analytics:read')"
    ))
    op.execute(sa.text("DELETE FROM permissions WHERE code = 'analytics:read'"))
    op.drop_table('area_score_backtest_reports')
