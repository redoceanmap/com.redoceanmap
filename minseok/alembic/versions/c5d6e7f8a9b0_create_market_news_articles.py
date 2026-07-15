"""market_news_articles — 상권 뉴스 수집·RAG 코퍼스 (market 스포크 소유).

주식 news_articles와 별개 코퍼스: 조인 키가 종목(ticker)이 아니라 지역 어간(area_tag).
임베딩은 bge-m3 1024차원 nullable(실패 시 NULL — 수집 우선, 다음 주기 재시도).
벡터 인덱스 없음(수천 건 브루트포스가 ms 단위) — 10만 건 이상이면 hnsw 재검토.

Revision ID: c5d6e7f8a9b0
Revises: b4c5d6e7f8a9
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = 'c5d6e7f8a9b0'
down_revision: Union[str, Sequence[str], None] = 'b4c5d6e7f8a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.create_table(
        'market_news_articles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False, server_default=''),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('area_tag', sa.String(length=50), nullable=False, server_default=''),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('embedding', Vector(1024), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(),
                  nullable=False),
        sa.UniqueConstraint('url', 'area_tag', name='uq_market_news_articles_url_area'),
    )
    op.create_index('ix_market_news_articles_area_tag', 'market_news_articles', ['area_tag'])
    op.create_index('ix_market_news_articles_published_at', 'market_news_articles',
                    ['published_at'])


def downgrade() -> None:
    op.drop_table('market_news_articles')
