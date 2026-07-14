"""create news_labels

뉴스 LLM 라벨(감성·이벤트·확신도) 저장 — 학습 피처용. 정답은 실현 수익률(price_bars 조인).
(news_id, labeler) 유니크 — 라벨러 버전별 재라벨링을 별도 행으로 공존시킨다.

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-07-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, Sequence[str], None] = 'd0e1f2a3b4c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'news_labels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('news_id', sa.Integer(), nullable=False),
        sa.Column('labeler', sa.String(length=40), nullable=False),
        sa.Column('sentiment', sa.Float(), nullable=False),
        sa.Column('event_type', sa.String(length=30), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['news_id'], ['news_articles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('news_id', 'labeler', name='uq_news_labels_news_id_labeler'),
    )
    op.create_index(op.f('ix_news_labels_news_id'), 'news_labels', ['news_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_news_labels_news_id'), table_name='news_labels')
    op.drop_table('news_labels')
