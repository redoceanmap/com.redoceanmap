"""add ticker to news_articles

학습 라벨 조인 키(ticker)를 구조화 컬럼으로 승격 — 제목 접두 [종목명] 방식 폐기.
같은 기사(url)라도 종목별 관련성은 별개 샘플이므로 유니크를 url → (url, ticker)로 확장.
기존 행은 제목 접두에서 ticker를 백필하고 접두를 벗겨 원문 제목으로 되돌린다.

Revision ID: c0d1e2f3a4b5
Revises: b8c9d0e1f2a3
Create Date: 2026-07-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0d1e2f3a4b5'
down_revision: Union[str, Sequence[str], None] = 'b8c9d0e1f2a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 그간 수집 실행에 쓰인 접두 종목명 → 티커 (백필 전용)
_NAME_TO_TICKER = {
    "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "현대차": "005380.KS",
    "LG에너지솔루션": "373220.KS", "NAVER": "035420.KS", "카카오": "035720.KS",
    "셀트리온": "068270.KS", "기아": "000270.KS", "POSCO홀딩스": "005490.KS",
    "KB금융": "105560.KS", "애플": "AAPL", "마이크로소프트": "MSFT", "엔비디아": "NVDA",
    "알파벳": "GOOGL", "아마존": "AMZN", "메타": "META", "테슬라": "TSLA",
    "브로드컴": "AVGO", "TSMC": "TSM", "ASML": "ASML", "오라클": "ORCL",
    "넷플릭스": "NFLX", "AMD": "AMD", "인텔": "INTC", "퀄컴": "QCOM",
    "마이크론": "MU", "세일즈포스": "CRM", "어도비": "ADBE", "팔란티어": "PLTR",
    "ARM홀딩스": "ARM",
}


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'news_articles',
        sa.Column('ticker', sa.String(length=20), nullable=False, server_default=''),
    )
    op.create_index(op.f('ix_news_articles_ticker'), 'news_articles', ['ticker'], unique=False)

    # 백필 — 접두 [종목명]에서 ticker 추출 후 제목을 원문으로 복원
    for name, ticker in _NAME_TO_TICKER.items():
        prefix = f"[{name}] "
        op.execute(
            "UPDATE news_articles "
            f"SET ticker = '{ticker}', title = substr(title, char_length('{prefix}') + 1) "
            f"WHERE title LIKE '{prefix}%'"
        )

    op.drop_constraint('news_articles_url_key', 'news_articles', type_='unique')
    op.create_unique_constraint(
        'uq_news_articles_url_ticker', 'news_articles', ['url', 'ticker']
    )


def downgrade() -> None:
    """Downgrade schema. (제목 접두 복원은 하지 않는다 — ticker 정보만 컬럼에서 소실)"""
    op.drop_constraint('uq_news_articles_url_ticker', 'news_articles', type_='unique')
    # url 전역 유니크 복원 전에 중복 url 정리(최소 id 유지)
    op.execute(
        "DELETE FROM news_articles a USING news_articles b "
        "WHERE a.url = b.url AND a.id > b.id"
    )
    op.create_unique_constraint('news_articles_url_key', 'news_articles', ['url'])
    op.drop_index(op.f('ix_news_articles_ticker'), table_name='news_articles')
    op.drop_column('news_articles', 'ticker')
