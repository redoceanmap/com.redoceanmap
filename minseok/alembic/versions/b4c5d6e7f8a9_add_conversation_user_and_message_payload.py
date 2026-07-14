"""대화 히스토리용 컬럼 — conversations.user_id(소유자) + messages.payload(구조화 카드).

user_id는 nullable(익명/구버전 대화는 NULL, FK 없음 — auth 스포크와 DB 레벨 결합 회피).
payload는 답변에 곁들인 추천 상권/종목 카드 JSON — 히스토리 재진입 시 카드 복원용.

Revision ID: b4c5d6e7f8a9
Revises: a3b4c5d6e7f8
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = 'b4c5d6e7f8a9'
down_revision: Union[str, Sequence[str], None] = 'a3b4c5d6e7f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('conversations', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.add_column('messages', sa.Column('payload', JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column('messages', 'payload')
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_column('conversations', 'user_id')
