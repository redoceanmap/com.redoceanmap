"""market 소유 테이블 2종 추가 — 상권 뉴스 코퍼스 + 점수 백테스트 리포트.

런타임 전환(메인 DB → 전용 :5434) 준비: 루트 체인에만 있던 market_news_articles
(c5d6e7f8a9b0 + url Text 확장 d6e7f8a9b0c1)와 area_score_backtest_reports(c1d2e3f4a5b6 —
단, analytics:read 권한 시드는 auth 소유라 여기서 제외)를 독립 체인에 최종 스키마로 편입.
vector 확장은 init(7c5cfbd1c35f)에서 이미 생성됨.

Revision ID: 8d6efce2a41b
Revises: 7c5cfbd1c35f
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = '8d6efce2a41b'
down_revision: Union[str, Sequence[str], None] = '7c5cfbd1c35f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'market_news_articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('area_tag', sa.String(length=50), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('embedding', Vector(1024), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url', 'area_tag', name='uq_market_news_articles_url_area'),
    )
    op.create_index(op.f('ix_market_news_articles_area_tag'), 'market_news_articles', ['area_tag'], unique=False)
    op.create_index(op.f('ix_market_news_articles_published_at'), 'market_news_articles', ['published_at'], unique=False)

    op.create_table(
        'area_score_backtest_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ran_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('params', postgresql.JSONB(), nullable=False),
        sa.Column('payload', postgresql.JSONB(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('area_score_backtest_reports')
    op.drop_index(op.f('ix_market_news_articles_published_at'), table_name='market_news_articles')
    op.drop_index(op.f('ix_market_news_articles_area_tag'), table_name='market_news_articles')
    op.drop_table('market_news_articles')
