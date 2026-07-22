"""forecast_snapshots에 레짐·어닝 veto 컬럼 — 사후 레짐별 적중률 분석의 재료.

regime: 캡처 시점 시장 레짐(BULL/BEAR/HIGH_VOL, 지수 미수집이면 NULL).
regime_conditional: 확률·밴드가 레짐 조건부 통계였는지.
earnings_veto: 실적 발표 ±2일 관망 강등 여부(NEUTRAL 저장 → hit NULL 자동 제외).

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'd2e3f4a5b6c7'
down_revision: Union[str, Sequence[str], None] = 'c1d2e3f4a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('forecast_snapshots', sa.Column('regime', sa.String(length=10), nullable=True))
    op.add_column('forecast_snapshots', sa.Column(
        'regime_conditional', sa.Boolean(), server_default=sa.text('false'), nullable=False,
    ))
    op.add_column('forecast_snapshots', sa.Column(
        'earnings_veto', sa.Boolean(), server_default=sa.text('false'), nullable=False,
    ))


def downgrade() -> None:
    op.drop_column('forecast_snapshots', 'earnings_veto')
    op.drop_column('forecast_snapshots', 'regime_conditional')
    op.drop_column('forecast_snapshots', 'regime')
