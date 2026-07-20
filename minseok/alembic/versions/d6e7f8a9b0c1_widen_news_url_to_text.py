"""widen news url to text

수집 URL 길이 초과로 적재 배치가 통째로 롤백되던 문제를 푼다.
Google News RSS는 검색 쿼리를 base64로 감싼 URL을 돌려줘, 한글 검색어(국내 대형주·상권)에서
1000자를 넘는 개체가 간헐적으로 나온다(실측 최장 988/1000 — 경계선). String(1000) →
Text로 확장해 유니크 btree 인덱스 한계(~2704 bytes)까지 천장을 올린다.

유니크 제약(url, ticker) / (url, area_tag)은 그대로 둔다 — 컬럼 타입만 바꾼다.

Revision ID: d6e7f8a9b0c1
Revises: c5d6e7f8a9b0
Create Date: 2026-07-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6e7f8a9b0c1'
down_revision: Union[str, Sequence[str], None] = 'c5d6e7f8a9b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'news_articles', 'url',
        existing_type=sa.String(length=1000), type_=sa.Text(), existing_nullable=False,
    )
    op.alter_column(
        'market_news_articles', 'url',
        existing_type=sa.String(length=1000), type_=sa.Text(), existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema. (1000자 초과 행은 되돌릴 수 없어 삭제한다)"""
    op.execute("DELETE FROM news_articles WHERE char_length(url) > 1000")
    op.execute("DELETE FROM market_news_articles WHERE char_length(url) > 1000")
    op.alter_column(
        'market_news_articles', 'url',
        existing_type=sa.Text(), type_=sa.String(length=1000), existing_nullable=False,
    )
    op.alter_column(
        'news_articles', 'url',
        existing_type=sa.Text(), type_=sa.String(length=1000), existing_nullable=False,
    )
