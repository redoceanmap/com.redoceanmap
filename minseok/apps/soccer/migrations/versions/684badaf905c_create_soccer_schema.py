"""create_soccer_schema

Revision ID: 684badaf905c
Revises: 67f72486c954
Create Date: 2026-07-13 14:56:15.800484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '684badaf905c'
down_revision: Union[str, Sequence[str], None] = '67f72486c954'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ERD 원문 유지 — statdium_name 오탈자 포함 (soccer-database.md 4장)
    op.create_table(
        "stadium",
        sa.Column("stadium_id", sa.String(10), primary_key=True),
        sa.Column("statdium_name", sa.String(40), nullable=False),
        sa.Column("hometeam_id", sa.String(10)),
        sa.Column("seat_count", sa.Integer),
        sa.Column("address", sa.String(60)),
        sa.Column("ddd", sa.String(10)),
        sa.Column("tel", sa.String(10)),
    )

    op.create_table(
        "team",
        sa.Column("team_id", sa.String(10), primary_key=True),
        sa.Column("region_name", sa.String(10), nullable=False),
        sa.Column("team_name", sa.String(40)),
        sa.Column("e_team_name", sa.String(50)),
        sa.Column("orig_yyyy", sa.String(10)),
        sa.Column("zip_code1", sa.String(10)),
        sa.Column("zip_code2", sa.String(10)),
        sa.Column("address", sa.String(80)),
        sa.Column("ddd", sa.String(10)),
        sa.Column("tel", sa.String(10)),
        sa.Column("fax", sa.String(10)),
        sa.Column("homepage", sa.String(50)),
        sa.Column("owner", sa.String(10)),
        sa.Column("stadium_id", sa.String(10), nullable=True),
        sa.ForeignKeyConstraint(
            ["stadium_id"], ["stadium.stadium_id"],
            onupdate="CASCADE", ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_team_stadium_id", "team", ["stadium_id"])

    op.create_table(
        "player",
        sa.Column("player_id", sa.String(10), primary_key=True),
        sa.Column("player_name", sa.String(20), nullable=False),
        sa.Column("e_player_name", sa.String(40)),
        sa.Column("nickname", sa.String(30)),
        sa.Column("join_yyyy", sa.String(10)),
        sa.Column("position", sa.String(10)),
        sa.Column("back_no", sa.Integer),
        sa.Column("nation", sa.String(20)),
        sa.Column("birth_date", sa.Date),
        sa.Column("solar", sa.String(10)),
        sa.Column("height", sa.Integer),
        sa.Column("weight", sa.Integer),
        sa.Column("team_id", sa.String(10), nullable=True),
        sa.ForeignKeyConstraint(
            ["team_id"], ["team.team_id"],
            onupdate="CASCADE", ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_player_team_id", "player", ["team_id"])

    op.create_table(
        "schedule",
        sa.Column("sche_date", sa.String(10), primary_key=True),
        sa.Column("stadium_id", sa.String(10), primary_key=True),
        sa.Column("gubun", sa.String(10)),
        sa.Column("hometeam_id", sa.String(10)),
        sa.Column("awayteam_id", sa.String(10)),
        sa.Column("home_score", sa.Integer),
        sa.Column("away_score", sa.Integer),
        sa.ForeignKeyConstraint(
            ["stadium_id"], ["stadium.stadium_id"],
            onupdate="CASCADE", ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_schedule_stadium_id", "schedule", ["stadium_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_schedule_stadium_id", table_name="schedule")
    op.drop_table("schedule")
    op.drop_index("ix_player_team_id", table_name="player")
    op.drop_table("player")
    op.drop_index("ix_team_stadium_id", table_name="team")
    op.drop_table("team")
    op.drop_table("stadium")
