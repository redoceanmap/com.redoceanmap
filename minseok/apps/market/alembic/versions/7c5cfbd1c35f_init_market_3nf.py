"""init market 3nf

Revision ID: 7c5cfbd1c35f
Revises:
Create Date: 2026-07-13 15:32:36.082839

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c5cfbd1c35f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # pgvector 확장만 활성화 — ERD에 벡터 컬럼 없음 (market-database.md §1)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ── 차원 (market-database.md §4.3 순서) ─────────────────────────
    op.create_table('region',
    sa.Column('code', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.Column('parent_code', sa.String(length=20), nullable=True),
    sa.Column('x_coord', sa.Integer(), nullable=True),
    sa.Column('y_coord', sa.Integer(), nullable=True),
    sa.Column('area_size', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_index(op.f('ix_region_parent_code'), 'region', ['parent_code'], unique=False)
    # 자기참조 FK는 테이블 생성 후 분리 생성 (§4.3 region)
    op.create_foreign_key('region_parent_code_fkey', 'region', 'region', ['parent_code'], ['code'])

    op.create_table('trade_area_division',
    sa.Column('code', sa.String(length=2), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_table('service_category',
    sa.Column('code', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_table('change_indicator',
    sa.Column('code', sa.String(length=4), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_table('trade_area',
    sa.Column('code', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('division_code', sa.String(length=2), nullable=False),
    sa.Column('region_code', sa.String(length=20), nullable=True),
    sa.Column('x_coord', sa.Integer(), nullable=False),
    sa.Column('y_coord', sa.Integer(), nullable=False),
    sa.Column('area_size', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['division_code'], ['trade_area_division.code'], ),
    sa.ForeignKeyConstraint(['region_code'], ['region.code'], ),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_index(op.f('ix_trade_area_division_code'), 'trade_area', ['division_code'], unique=False)
    op.create_index(op.f('ix_trade_area_region_code'), 'trade_area', ['region_code'], unique=False)

    # ── 팩트 8 ──────────────────────────────────────────────────────
    op.create_table('estimated_sales',
    sa.Column('service_code', sa.String(length=20), nullable=False),
    sa.Column('monthly_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('monthly_sales_count', sa.Integer(), nullable=False),
    sa.Column('weekday_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('weekend_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('mon_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('tue_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('wed_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('thu_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('fri_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('sat_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('sun_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('time_00_06_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('time_06_11_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('time_11_14_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('time_14_17_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('time_17_21_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('time_21_24_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('male_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('female_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('age_10_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('age_20_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('age_30_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('age_40_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('age_50_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('age_60_plus_sales_amount', sa.BigInteger(), nullable=False),
    sa.Column('weekday_sales_count', sa.Integer(), nullable=False),
    sa.Column('weekend_sales_count', sa.Integer(), nullable=False),
    sa.Column('mon_sales_count', sa.Integer(), nullable=False),
    sa.Column('tue_sales_count', sa.Integer(), nullable=False),
    sa.Column('wed_sales_count', sa.Integer(), nullable=False),
    sa.Column('thu_sales_count', sa.Integer(), nullable=False),
    sa.Column('fri_sales_count', sa.Integer(), nullable=False),
    sa.Column('sat_sales_count', sa.Integer(), nullable=False),
    sa.Column('sun_sales_count', sa.Integer(), nullable=False),
    sa.Column('time_00_06_sales_count', sa.Integer(), nullable=False),
    sa.Column('time_06_11_sales_count', sa.Integer(), nullable=False),
    sa.Column('time_11_14_sales_count', sa.Integer(), nullable=False),
    sa.Column('time_14_17_sales_count', sa.Integer(), nullable=False),
    sa.Column('time_17_21_sales_count', sa.Integer(), nullable=False),
    sa.Column('time_21_24_sales_count', sa.Integer(), nullable=False),
    sa.Column('male_sales_count', sa.Integer(), nullable=False),
    sa.Column('female_sales_count', sa.Integer(), nullable=False),
    sa.Column('age_10_sales_count', sa.Integer(), nullable=False),
    sa.Column('age_20_sales_count', sa.Integer(), nullable=False),
    sa.Column('age_30_sales_count', sa.Integer(), nullable=False),
    sa.Column('age_40_sales_count', sa.Integer(), nullable=False),
    sa.Column('age_50_sales_count', sa.Integer(), nullable=False),
    sa.Column('age_60_plus_sales_count', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year_quarter', sa.Integer(), nullable=False),
    sa.Column('trdar_code', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['service_code'], ['service_category.code'], ),
    sa.ForeignKeyConstraint(['trdar_code'], ['trade_area.code'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('year_quarter', 'trdar_code', 'service_code', name='uq_estimated_sales')
    )
    op.create_index(op.f('ix_estimated_sales_service_code'), 'estimated_sales', ['service_code'], unique=False)
    op.create_index(op.f('ix_estimated_sales_trdar_code'), 'estimated_sales', ['trdar_code'], unique=False)
    op.create_index(op.f('ix_estimated_sales_year_quarter'), 'estimated_sales', ['year_quarter'], unique=False)
    op.create_table('store',
    sa.Column('service_code', sa.String(length=20), nullable=False),
    sa.Column('store_count', sa.Integer(), nullable=False),
    sa.Column('similar_industry_store_count', sa.Integer(), nullable=False),
    sa.Column('opening_rate', sa.Integer(), nullable=False),
    sa.Column('opening_store_count', sa.Integer(), nullable=False),
    sa.Column('closure_rate', sa.Integer(), nullable=False),
    sa.Column('closure_store_count', sa.Integer(), nullable=False),
    sa.Column('franchise_store_count', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year_quarter', sa.Integer(), nullable=False),
    sa.Column('trdar_code', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['service_code'], ['service_category.code'], ),
    sa.ForeignKeyConstraint(['trdar_code'], ['trade_area.code'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('year_quarter', 'trdar_code', 'service_code', name='uq_store')
    )
    op.create_index(op.f('ix_store_service_code'), 'store', ['service_code'], unique=False)
    op.create_index(op.f('ix_store_trdar_code'), 'store', ['trdar_code'], unique=False)
    op.create_index(op.f('ix_store_year_quarter'), 'store', ['year_quarter'], unique=False)
    op.create_table('floating_population',
    sa.Column('total_floating_pop', sa.Integer(), nullable=False),
    sa.Column('male_floating_pop', sa.Integer(), nullable=False),
    sa.Column('female_floating_pop', sa.Integer(), nullable=False),
    sa.Column('age_10_floating_pop', sa.Integer(), nullable=False),
    sa.Column('age_20_floating_pop', sa.Integer(), nullable=False),
    sa.Column('age_30_floating_pop', sa.Integer(), nullable=False),
    sa.Column('age_40_floating_pop', sa.Integer(), nullable=False),
    sa.Column('age_50_floating_pop', sa.Integer(), nullable=False),
    sa.Column('age_60_plus_floating_pop', sa.Integer(), nullable=False),
    sa.Column('time_00_06_floating_pop', sa.Integer(), nullable=False),
    sa.Column('time_06_11_floating_pop', sa.Integer(), nullable=False),
    sa.Column('time_11_14_floating_pop', sa.Integer(), nullable=False),
    sa.Column('time_14_17_floating_pop', sa.Integer(), nullable=False),
    sa.Column('time_17_21_floating_pop', sa.Integer(), nullable=False),
    sa.Column('time_21_24_floating_pop', sa.Integer(), nullable=False),
    sa.Column('mon_floating_pop', sa.Integer(), nullable=False),
    sa.Column('tue_floating_pop', sa.Integer(), nullable=False),
    sa.Column('wed_floating_pop', sa.Integer(), nullable=False),
    sa.Column('thu_floating_pop', sa.Integer(), nullable=False),
    sa.Column('fri_floating_pop', sa.Integer(), nullable=False),
    sa.Column('sat_floating_pop', sa.Integer(), nullable=False),
    sa.Column('sun_floating_pop', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year_quarter', sa.Integer(), nullable=False),
    sa.Column('trdar_code', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['trdar_code'], ['trade_area.code'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('year_quarter', 'trdar_code', name='uq_floating_population')
    )
    op.create_index(op.f('ix_floating_population_trdar_code'), 'floating_population', ['trdar_code'], unique=False)
    op.create_index(op.f('ix_floating_population_year_quarter'), 'floating_population', ['year_quarter'], unique=False)
    op.create_table('resident_population',
    sa.Column('total_resident_pop', sa.Integer(), nullable=False),
    sa.Column('male_resident_pop', sa.Integer(), nullable=False),
    sa.Column('female_resident_pop', sa.Integer(), nullable=False),
    sa.Column('age_10_resident_pop', sa.Integer(), nullable=False),
    sa.Column('age_20_resident_pop', sa.Integer(), nullable=False),
    sa.Column('age_30_resident_pop', sa.Integer(), nullable=False),
    sa.Column('age_40_resident_pop', sa.Integer(), nullable=False),
    sa.Column('age_50_resident_pop', sa.Integer(), nullable=False),
    sa.Column('age_60_plus_resident_pop', sa.Integer(), nullable=False),
    sa.Column('male_age_10_resident_pop', sa.Integer(), nullable=False),
    sa.Column('male_age_20_resident_pop', sa.Integer(), nullable=False),
    sa.Column('male_age_30_resident_pop', sa.Integer(), nullable=False),
    sa.Column('male_age_40_resident_pop', sa.Integer(), nullable=False),
    sa.Column('male_age_50_resident_pop', sa.Integer(), nullable=False),
    sa.Column('male_age_60_plus_resident_pop', sa.Integer(), nullable=False),
    sa.Column('female_age_10_resident_pop', sa.Integer(), nullable=False),
    sa.Column('female_age_20_resident_pop', sa.Integer(), nullable=False),
    sa.Column('female_age_30_resident_pop', sa.Integer(), nullable=False),
    sa.Column('female_age_40_resident_pop', sa.Integer(), nullable=False),
    sa.Column('female_age_50_resident_pop', sa.Integer(), nullable=False),
    sa.Column('female_age_60_plus_resident_pop', sa.Integer(), nullable=False),
    sa.Column('total_household_count', sa.Integer(), nullable=False),
    sa.Column('apartment_household_count', sa.Integer(), nullable=False),
    sa.Column('non_apartment_household_count', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year_quarter', sa.Integer(), nullable=False),
    sa.Column('trdar_code', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['trdar_code'], ['trade_area.code'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('year_quarter', 'trdar_code', name='uq_resident_population')
    )
    op.create_index(op.f('ix_resident_population_trdar_code'), 'resident_population', ['trdar_code'], unique=False)
    op.create_index(op.f('ix_resident_population_year_quarter'), 'resident_population', ['year_quarter'], unique=False)
    op.create_table('working_population',
    sa.Column('total_working_pop', sa.Integer(), nullable=False),
    sa.Column('male_working_pop', sa.Integer(), nullable=False),
    sa.Column('female_working_pop', sa.Integer(), nullable=False),
    sa.Column('age_10_working_pop', sa.Integer(), nullable=False),
    sa.Column('age_20_working_pop', sa.Integer(), nullable=False),
    sa.Column('age_30_working_pop', sa.Integer(), nullable=False),
    sa.Column('age_40_working_pop', sa.Integer(), nullable=False),
    sa.Column('age_50_working_pop', sa.Integer(), nullable=False),
    sa.Column('age_60_plus_working_pop', sa.Integer(), nullable=False),
    sa.Column('male_age_10_working_pop', sa.Integer(), nullable=False),
    sa.Column('male_age_20_working_pop', sa.Integer(), nullable=False),
    sa.Column('male_age_30_working_pop', sa.Integer(), nullable=False),
    sa.Column('male_age_40_working_pop', sa.Integer(), nullable=False),
    sa.Column('male_age_50_working_pop', sa.Integer(), nullable=False),
    sa.Column('male_age_60_plus_working_pop', sa.Integer(), nullable=False),
    sa.Column('female_age_10_working_pop', sa.Integer(), nullable=False),
    sa.Column('female_age_20_working_pop', sa.Integer(), nullable=False),
    sa.Column('female_age_30_working_pop', sa.Integer(), nullable=False),
    sa.Column('female_age_40_working_pop', sa.Integer(), nullable=False),
    sa.Column('female_age_50_working_pop', sa.Integer(), nullable=False),
    sa.Column('female_age_60_plus_working_pop', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year_quarter', sa.Integer(), nullable=False),
    sa.Column('trdar_code', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['trdar_code'], ['trade_area.code'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('year_quarter', 'trdar_code', name='uq_working_population')
    )
    op.create_index(op.f('ix_working_population_trdar_code'), 'working_population', ['trdar_code'], unique=False)
    op.create_index(op.f('ix_working_population_year_quarter'), 'working_population', ['year_quarter'], unique=False)
    op.create_table('consumption',
    sa.Column('monthly_avg_income', sa.Float(), nullable=True),
    sa.Column('income_range_code', sa.Integer(), nullable=True),
    sa.Column('total_expenditure', sa.Float(), nullable=True),
    sa.Column('food_expenditure', sa.Float(), nullable=True),
    sa.Column('clothing_expenditure', sa.Float(), nullable=True),
    sa.Column('household_expenditure', sa.Float(), nullable=True),
    sa.Column('medical_expenditure', sa.Float(), nullable=True),
    sa.Column('transport_expenditure', sa.Float(), nullable=True),
    sa.Column('leisure_expenditure', sa.Float(), nullable=True),
    sa.Column('culture_expenditure', sa.Float(), nullable=True),
    sa.Column('education_expenditure', sa.Float(), nullable=True),
    sa.Column('entertainment_expenditure', sa.Float(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year_quarter', sa.Integer(), nullable=False),
    sa.Column('trdar_code', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['trdar_code'], ['trade_area.code'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('year_quarter', 'trdar_code', name='uq_consumption')
    )
    op.create_index(op.f('ix_consumption_trdar_code'), 'consumption', ['trdar_code'], unique=False)
    op.create_index(op.f('ix_consumption_year_quarter'), 'consumption', ['year_quarter'], unique=False)
    op.create_table('apartment',
    sa.Column('complex_count', sa.Integer(), nullable=False),
    sa.Column('area_under_66_count', sa.Integer(), nullable=True),
    sa.Column('area_66_count', sa.Integer(), nullable=True),
    sa.Column('area_99_count', sa.Integer(), nullable=True),
    sa.Column('area_132_count', sa.Integer(), nullable=True),
    sa.Column('area_165_count', sa.Integer(), nullable=True),
    sa.Column('price_under_1b_count', sa.Integer(), nullable=True),
    sa.Column('price_1b_count', sa.Integer(), nullable=True),
    sa.Column('price_2b_count', sa.Integer(), nullable=True),
    sa.Column('price_3b_count', sa.Integer(), nullable=True),
    sa.Column('price_4b_count', sa.Integer(), nullable=True),
    sa.Column('price_5b_count', sa.Integer(), nullable=True),
    sa.Column('price_over_6b_count', sa.Integer(), nullable=True),
    sa.Column('avg_area', sa.Integer(), nullable=False),
    sa.Column('avg_price', sa.BigInteger(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year_quarter', sa.Integer(), nullable=False),
    sa.Column('trdar_code', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['trdar_code'], ['trade_area.code'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('year_quarter', 'trdar_code', name='uq_apartment')
    )
    op.create_index(op.f('ix_apartment_trdar_code'), 'apartment', ['trdar_code'], unique=False)
    op.create_index(op.f('ix_apartment_year_quarter'), 'apartment', ['year_quarter'], unique=False)
    op.create_table('commercial_change',
    sa.Column('change_indicator', sa.String(length=4), nullable=False),
    sa.Column('operating_months_avg', sa.Integer(), nullable=False),
    sa.Column('closure_months_avg', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year_quarter', sa.Integer(), nullable=False),
    sa.Column('trdar_code', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['change_indicator'], ['change_indicator.code'], ),
    sa.ForeignKeyConstraint(['trdar_code'], ['trade_area.code'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('year_quarter', 'trdar_code', name='uq_commercial_change')
    )
    op.create_index(op.f('ix_commercial_change_trdar_code'), 'commercial_change', ['trdar_code'], unique=False)
    op.create_index(op.f('ix_commercial_change_year_quarter'), 'commercial_change', ['year_quarter'], unique=False)

    # ── 벤치마크 (상권 팩트 아님 — trdar_code 없음) ─────────────────
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


def downgrade() -> None:
    """Downgrade schema. upgrade의 정확한 역순 — extension은 drop하지 않는다."""
    op.drop_index(op.f('ix_commercial_change_benchmark_year_quarter'), table_name='commercial_change_benchmark')
    op.drop_index(op.f('ix_commercial_change_benchmark_region_code'), table_name='commercial_change_benchmark')
    op.drop_table('commercial_change_benchmark')
    op.drop_index(op.f('ix_commercial_change_year_quarter'), table_name='commercial_change')
    op.drop_index(op.f('ix_commercial_change_trdar_code'), table_name='commercial_change')
    op.drop_table('commercial_change')
    op.drop_index(op.f('ix_apartment_year_quarter'), table_name='apartment')
    op.drop_index(op.f('ix_apartment_trdar_code'), table_name='apartment')
    op.drop_table('apartment')
    op.drop_index(op.f('ix_consumption_year_quarter'), table_name='consumption')
    op.drop_index(op.f('ix_consumption_trdar_code'), table_name='consumption')
    op.drop_table('consumption')
    op.drop_index(op.f('ix_working_population_year_quarter'), table_name='working_population')
    op.drop_index(op.f('ix_working_population_trdar_code'), table_name='working_population')
    op.drop_table('working_population')
    op.drop_index(op.f('ix_resident_population_year_quarter'), table_name='resident_population')
    op.drop_index(op.f('ix_resident_population_trdar_code'), table_name='resident_population')
    op.drop_table('resident_population')
    op.drop_index(op.f('ix_floating_population_year_quarter'), table_name='floating_population')
    op.drop_index(op.f('ix_floating_population_trdar_code'), table_name='floating_population')
    op.drop_table('floating_population')
    op.drop_index(op.f('ix_store_year_quarter'), table_name='store')
    op.drop_index(op.f('ix_store_trdar_code'), table_name='store')
    op.drop_index(op.f('ix_store_service_code'), table_name='store')
    op.drop_table('store')
    op.drop_index(op.f('ix_estimated_sales_year_quarter'), table_name='estimated_sales')
    op.drop_index(op.f('ix_estimated_sales_trdar_code'), table_name='estimated_sales')
    op.drop_index(op.f('ix_estimated_sales_service_code'), table_name='estimated_sales')
    op.drop_table('estimated_sales')
    op.drop_index(op.f('ix_trade_area_region_code'), table_name='trade_area')
    op.drop_index(op.f('ix_trade_area_division_code'), table_name='trade_area')
    op.drop_table('trade_area')
    op.drop_table('change_indicator')
    op.drop_table('service_category')
    op.drop_table('trade_area_division')
    op.drop_constraint('region_parent_code_fkey', 'region', type_='foreignkey')
    op.drop_index(op.f('ix_region_parent_code'), table_name='region')
    op.drop_table('region')
