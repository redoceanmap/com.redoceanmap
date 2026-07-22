"""예측 스냅샷 테이블 — 일일 forecast(방향·확률·신호 분해)를 영속화해 사후 채점한다.

(ticker, horizon_days, as_of) 유니크 — 주말/재실행 시 ON CONFLICT로 자연 스킵(멱등).
확률·밴드 컬럼은 nullable(표본 0이면 probability가 None). 채점 컬럼(evaluated_at·
realized_*·hit)은 horizon 도래 후 채워진다 — hit은 UP→상승, DOWN→비상승 적중,
NEUTRAL은 NULL(방향 주장이 아니므로 적중률 분모 제외).

Revision ID: b0c1d2e3f4a5
Revises: a9b8c7d6e5f4
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = 'b0c1d2e3f4a5'
down_revision: Union[str, Sequence[str], None] = 'a9b8c7d6e5f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'forecast_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('as_of', sa.DateTime(timezone=True), nullable=False),
        sa.Column('horizon_days', sa.Integer(), nullable=False),
        sa.Column('direction', sa.String(length=8), nullable=False),
        sa.Column('base_price', sa.Float(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('signals', postgresql.JSONB(), nullable=False),
        sa.Column('up_rate', sa.Float(), nullable=True),
        sa.Column('sample_size', sa.Integer(), nullable=True),
        sa.Column('hits', sa.Integer(), nullable=True),
        sa.Column('ci_low', sa.Float(), nullable=True),
        sa.Column('ci_high', sa.Float(), nullable=True),
        sa.Column('baseline_up_rate', sa.Float(), nullable=True),
        sa.Column('ready', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('band_source', sa.String(length=10), nullable=True),
        sa.Column('q25_pct', sa.Float(), nullable=True),
        sa.Column('median_pct', sa.Float(), nullable=True),
        sa.Column('q75_pct', sa.Float(), nullable=True),
        sa.Column('evaluated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('realized_price', sa.Float(), nullable=True),
        sa.Column('realized_return_pct', sa.Float(), nullable=True),
        sa.Column('hit', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticker', 'horizon_days', 'as_of', name='uq_forecast_snapshots_ticker_horizon_as_of'),
    )
    op.create_index(op.f('ix_forecast_snapshots_ticker'), 'forecast_snapshots', ['ticker'], unique=False)
    # 채점 대기분 조회 전용 부분 인덱스 — 채점 완료가 쌓여도 pending 스캔이 좁게 유지된다
    op.create_index(
        'ix_forecast_snapshots_pending', 'forecast_snapshots', ['horizon_days'],
        unique=False, postgresql_where=sa.text('evaluated_at IS NULL'),
    )


def downgrade() -> None:
    op.drop_index('ix_forecast_snapshots_pending', table_name='forecast_snapshots')
    op.drop_index(op.f('ix_forecast_snapshots_ticker'), table_name='forecast_snapshots')
    op.drop_table('forecast_snapshots')
