"""create_inbound_mails_table

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'inbound_mails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.String(length=200), nullable=False),
        sa.Column('subject', sa.Text(), nullable=False),
        sa.Column('sender', sa.String(length=300), nullable=False),
        sa.Column('recipient', sa.String(length=300), nullable=False),
        sa.Column('preview', sa.Text(), nullable=False),
        sa.Column('received_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('inbound_mails')
