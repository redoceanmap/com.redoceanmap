import os
import sys
from pathlib import Path
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from alembic import context

# minseok/ 와 minseok/apps 를 경로에 올려 core.* 및 앱 ORM(chat, market...)을 import 가능하게 한다.
# (main.py 의 sys.path.insert(0, "apps") 와 동일 맥락 — 도커 백엔드의 자동 alembic 실행 포함)
_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(_ROOT / "apps"))
sys.path.insert(0, str(_ROOT))

load_dotenv(Path(__file__).parents[2] / ".env")

config = context.config
config.set_main_option(
    "sqlalchemy.url",
    os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg://"),
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from core.database import Base
import auth.adapter.outbound.orm.user_orm  # noqa: F401
import auth.adapter.outbound.orm.refresh_token_orm  # noqa: F401
import market.adapter.outbound.orm.region_orm  # noqa: F401
import market.adapter.outbound.orm.trade_area_division_orm  # noqa: F401
import market.adapter.outbound.orm.service_category_orm  # noqa: F401
import market.adapter.outbound.orm.change_indicator_orm  # noqa: F401
import market.adapter.outbound.orm.trade_area_orm  # noqa: F401
import market.adapter.outbound.orm.estimated_sales_orm  # noqa: F401
import market.adapter.outbound.orm.store_orm  # noqa: F401
import market.adapter.outbound.orm.floating_population_orm  # noqa: F401
import market.adapter.outbound.orm.resident_population_orm  # noqa: F401
import market.adapter.outbound.orm.consumption_orm  # noqa: F401
import market.adapter.outbound.orm.working_population_orm  # noqa: F401
import market.adapter.outbound.orm.apartment_orm  # noqa: F401
import market.adapter.outbound.orm.commercial_change_orm  # noqa: F401
import market.adapter.outbound.orm.commercial_change_benchmark_orm  # noqa: F401
import chat.adapter.outbound.orm.conversation_orm  # noqa: F401
import recommendation.adapter.outbound.orm.recommendation_orm  # noqa: F401
import stock.adapter.outbound.orm.news_article_orm  # noqa: F401
import stock.adapter.outbound.orm.price_bar_orm  # noqa: F401
import stock.adapter.outbound.orm.news_label_orm  # noqa: F401
import stock.adapter.outbound.orm.fundamental_snapshot_orm  # noqa: F401
import mail.adapter.outbound.orm.inbound_mail_orm  # noqa: F401

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
