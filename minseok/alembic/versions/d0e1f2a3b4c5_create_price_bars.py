"""create price_bars

뉴스↔주가 반응 라벨링용 OHLCV 저장 — 5분봉(단기 반응)·일봉(익일/주간).
ts는 봉 시작 시각(UTC)으로 news_articles.published_at과 조인한다.
(ticker, timeframe, ts) 유니크가 겹침 창 재수집(멱등 upsert)의 축이다.

Revision ID: d0e1f2a3b4c5
Revises: c0d1e2f3a4b5
Create Date: 2026-07-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0e1f2a3b4c5'
down_revision: Union[str, Sequence[str], None] = 'c0d1e2f3a4b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'price_bars',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('timeframe', sa.String(length=5), nullable=False),
        sa.Column('ts', sa.DateTime(timezone=True), nullable=False),
        sa.Column('open', sa.Float(), nullable=False),
        sa.Column('high', sa.Float(), nullable=False),
        sa.Column('low', sa.Float(), nullable=False),
        sa.Column('close', sa.Float(), nullable=False),
        sa.Column('volume', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticker', 'timeframe', 'ts', name='uq_price_bars_ticker_timeframe_ts'),
    )
    op.create_index(op.f('ix_price_bars_ticker'), 'price_bars', ['ticker'], unique=False)
    op.create_index(op.f('ix_price_bars_ts'), 'price_bars', ['ts'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_price_bars_ts'), table_name='price_bars')
    op.drop_index(op.f('ix_price_bars_ticker'), table_name='price_bars')
    op.drop_table('price_bars')
