from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from hub.app.ports.output.news_label_storage_port import NewsLabelStoragePort
from stock.adapter.outbound.gateways.news_label_storage_gateway import NewsLabelStorageGateway
from stock.adapter.outbound.pg.news_label_pg_repository import NewsLabelPgRepository
from stock.app.use_cases.news_label_interactor import NewsLabelInteractor


def get_news_label_storage_gateway(db: AsyncSession = Depends(get_db)) -> NewsLabelStoragePort:
    """허브 NewsLabelStoragePort 구현 프로바이더 — main.py가 dependency_overrides로 주입."""
    return NewsLabelStorageGateway(
        use_case=NewsLabelInteractor(labels=NewsLabelPgRepository(session=db))
    )
