"""펀더멘털 스냅샷 테이블 — 수집기(yfinance+DART)가 허브 /automation/fundamentals로 적재.

(ticker, as_of, source) 유니크 — 소스별 값 대조를 별도 행으로 공존시킨다.
지표 컬럼은 전부 nullable(한국 종목은 yfinance가 PER/PBR/EPS를 안 준다).

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'f2a3b4c5d6e7'
down_revision: Union[str, Sequence[str], None] = 'e1f2a3b4c5d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'fundamental_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('as_of', sa.Date(), nullable=False),
        sa.Column('source', sa.String(length=10), nullable=False),
        sa.Column('per', sa.Float(), nullable=True),
        sa.Column('pbr', sa.Float(), nullable=True),
        sa.Column('roe', sa.Float(), nullable=True),
        sa.Column('debt_to_equity', sa.Float(), nullable=True),
        sa.Column('fcf', sa.Float(), nullable=True),
        sa.Column('market_cap', sa.Float(), nullable=True),
        sa.Column('eps', sa.Float(), nullable=True),
        sa.Column('bps', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticker', 'as_of', 'source', name='uq_fundamental_snapshots_ticker_as_of_source'),
    )
    op.create_index(op.f('ix_fundamental_snapshots_ticker'), 'fundamental_snapshots', ['ticker'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_fundamental_snapshots_ticker'), table_name='fundamental_snapshots')
    op.drop_table('fundamental_snapshots')
