"""split seoul benchmark from commercial_change

서울_운영/폐업_영업_개월_평균은 (year_quarter, trdar_code) 자연키 중 분기에만 종속
(부분 종속)이라 지역(시도) 단위 벤치마크 테이블로 분리한다. region에 시도(level0)
계층을 추가해 전국 확장 시 시도별 벤치마크 행이 늘어나는 구조로 만든다.

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-07-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, Sequence[str], None] = 'f6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SEOUL_SIDO_CODE = '11'


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('commercial_change_benchmark',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year_quarter', sa.Integer(), nullable=False),
    sa.Column('region_code', sa.String(length=20), nullable=False),
    sa.Column('operating_months_avg', sa.Integer(), nullable=False),
    sa.Column('closure_months_avg', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['region_code'], ['region.code'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('year_quarter', 'region_code', name='uq_commercial_change_benchmark')
    )
    op.create_index(op.f('ix_commercial_change_benchmark_region_code'), 'commercial_change_benchmark', ['region_code'], unique=False)
    op.create_index(op.f('ix_commercial_change_benchmark_year_quarter'), 'commercial_change_benchmark', ['year_quarter'], unique=False)

    # 데이터 이관 — 적재된 DB에만 해당(빈 DB는 ingest 스크립트가 시도부터 적재)
    op.execute(
        "INSERT INTO region (code, name, level, parent_code) "
        f"SELECT '{SEOUL_SIDO_CODE}', '서울특별시', 0, NULL "
        "WHERE EXISTS (SELECT 1 FROM region WHERE level = 1) "
        f"AND NOT EXISTS (SELECT 1 FROM region WHERE code = '{SEOUL_SIDO_CODE}')"
    )
    op.execute(
        f"UPDATE region SET parent_code = '{SEOUL_SIDO_CODE}' WHERE level = 1"
    )
    op.execute(
        "INSERT INTO commercial_change_benchmark "
        "(year_quarter, region_code, operating_months_avg, closure_months_avg) "
        f"SELECT year_quarter, '{SEOUL_SIDO_CODE}', "
        "MIN(seoul_operating_months_avg), MIN(seoul_closure_months_avg) "
        "FROM commercial_change GROUP BY year_quarter"
    )

    op.drop_column('commercial_change', 'seoul_operating_months_avg')
    op.drop_column('commercial_change', 'seoul_closure_months_avg')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('commercial_change', sa.Column('seoul_operating_months_avg', sa.Integer(), nullable=True))
    op.add_column('commercial_change', sa.Column('seoul_closure_months_avg', sa.Integer(), nullable=True))
    op.execute(
        "UPDATE commercial_change cc SET "
        "seoul_operating_months_avg = b.operating_months_avg, "
        "seoul_closure_months_avg = b.closure_months_avg "
        "FROM commercial_change_benchmark b "
        f"WHERE b.year_quarter = cc.year_quarter AND b.region_code = '{SEOUL_SIDO_CODE}'"
    )
    op.alter_column('commercial_change', 'seoul_operating_months_avg', nullable=False)
    op.alter_column('commercial_change', 'seoul_closure_months_avg', nullable=False)

    op.drop_index(op.f('ix_commercial_change_benchmark_year_quarter'), table_name='commercial_change_benchmark')
    op.drop_index(op.f('ix_commercial_change_benchmark_region_code'), table_name='commercial_change_benchmark')
    op.drop_table('commercial_change_benchmark')

    op.execute("UPDATE region SET parent_code = NULL WHERE level = 1")
    op.execute(f"DELETE FROM region WHERE code = '{SEOUL_SIDO_CODE}' AND level = 0")
