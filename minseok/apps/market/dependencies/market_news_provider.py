from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from hub.app.ports.output.market_news_search_port import MarketNewsSearchPort
from hub.app.ports.output.market_news_storage_port import MarketNewsStoragePort
from market.adapter.outbound.ai.ollama_embedding_adapter import OllamaEmbeddingAdapter
from market.adapter.outbound.gateways.market_news_search_gateway import MarketNewsSearchGateway
from market.adapter.outbound.gateways.market_news_storage_gateway import MarketNewsStorageGateway
from market.adapter.outbound.pg.market_news_pg_repository import MarketNewsPgRepository
from market.app.use_cases.market_news_interactor import MarketNewsInteractor


def get_market_news_storage_gateway(db: AsyncSession = Depends(get_db)) -> MarketNewsStoragePort:
    """허브 MarketNewsStoragePort 구현 프로바이더 — main.py가 dependency_overrides로 주입."""
    return MarketNewsStorageGateway(use_case=MarketNewsInteractor(
        news=MarketNewsPgRepository(session=db), embeddings=OllamaEmbeddingAdapter(),
    ))


def get_market_news_search_gateway(db: AsyncSession = Depends(get_db)) -> MarketNewsSearchPort:
    """허브 MarketNewsSearchPort 구현 프로바이더 — main.py가 dependency_overrides로 주입."""
    return MarketNewsSearchGateway(use_case=MarketNewsInteractor(
        news=MarketNewsPgRepository(session=db), embeddings=OllamaEmbeddingAdapter(),
    ))
