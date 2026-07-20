"""add user consent

약관 동의 증빙 컬럼 — 소셜/일반 가입 모두 필수 약관 동의 시각을 남긴다(개인정보보호법 동의 이력).
기존 유저는 NULL로 둔다(소급 동의 없음). marketing_agreed는 선택 동의라 기본 false.

Revision ID: e7f8a9b0c1d2
Revises: d6e7f8a9b0c1
Create Date: 2026-07-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7f8a9b0c1d2'
down_revision: Union[str, Sequence[str], None] = 'd6e7f8a9b0c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('terms_agreed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        'users',
        sa.Column('marketing_agreed', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'marketing_agreed')
    op.drop_column('users', 'terms_agreed_at')
