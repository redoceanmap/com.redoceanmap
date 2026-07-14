from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from hub.app.ports.output.news_search_port import NewsSearchPort
from hub.app.ports.output.news_storage_port import NewsStoragePort
from stock.adapter.outbound.ai.ollama_embedding_adapter import OllamaEmbeddingAdapter
from stock.adapter.outbound.gateways.news_search_gateway import NewsSearchGateway
from stock.adapter.outbound.gateways.news_storage_gateway import NewsStorageGateway
from stock.adapter.outbound.pg.news_pg_repository import NewsPgRepository
from stock.app.use_cases.news_interactor import NewsInteractor


def get_news_storage_gateway(db: AsyncSession = Depends(get_db)) -> NewsStoragePort:
    """허브 NewsStoragePort 구현 프로바이더 — main.py가 dependency_overrides로 주입."""
    return NewsStorageGateway(use_case=NewsInteractor(
        news=NewsPgRepository(session=db), embeddings=OllamaEmbeddingAdapter(),
    ))


def get_news_search_gateway(db: AsyncSession = Depends(get_db)) -> NewsSearchPort:
    """허브 NewsSearchPort 구현 프로바이더 — main.py가 dependency_overrides로 주입."""
    return NewsSearchGateway(use_case=NewsInteractor(
        news=NewsPgRepository(session=db), embeddings=OllamaEmbeddingAdapter(),
    ))
