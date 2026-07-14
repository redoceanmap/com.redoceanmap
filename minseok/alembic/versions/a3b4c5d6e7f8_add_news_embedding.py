"""news_articles에 제목 임베딩 컬럼(pgvector) — 뉴스 의미 검색(RAG)용.

bge-m3 1024차원, nullable(임베딩 실패 시 NULL — 수집 우선). 벡터 인덱스는 만들지 않는다:
수천 건 규모에서 브루트포스 코사인 스캔은 ms 단위라 ivfflat/hnsw가 순손실 —
10만 건 이상 쌓이면 hnsw 인덱스 추가를 재검토한다.

Revision ID: a3b4c5d6e7f8
Revises: f2a3b4c5d6e7
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = 'a3b4c5d6e7f8'
down_revision: Union[str, Sequence[str], None] = 'f2a3b4c5d6e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.add_column('news_articles', sa.Column('embedding', Vector(1024), nullable=True))


def downgrade() -> None:
    op.drop_column('news_articles', 'embedding')
