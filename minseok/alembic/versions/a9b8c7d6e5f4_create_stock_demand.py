"""분석 질문 수요 테이블 — StockInteractor가 기록, 워치리스트 수요 편입 스크립트가 소비.

ticker 유니크 upsert(질문마다 ask_count+1, last_asked_at 갱신).

Revision ID: a9b8c7d6e5f4
Revises: c3d4e5f6a7b8
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'a9b8c7d6e5f4'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'stock_demand',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('ask_count', sa.Integer(), nullable=False),
        sa.Column('last_asked_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticker', name='uq_stock_demand_ticker'),
    )
    op.create_index(op.f('ix_stock_demand_ticker'), 'stock_demand', ['ticker'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_stock_demand_ticker'), table_name='stock_demand')
    op.drop_table('stock_demand')
