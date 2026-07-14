from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from hub.app.ports.output.fundamental_storage_port import FundamentalStoragePort
from hub.app.ports.output.news_label_storage_port import NewsLabelStoragePort
from hub.app.ports.output.news_search_port import NewsSearchPort
from hub.app.ports.output.news_storage_port import NewsStoragePort
from hub.app.ports.output.price_bar_storage_port import PriceBarStoragePort
from hub.app.ports.output.stock_analysis_port import StockAnalysisPort
from stock.adapter.outbound.ai.ollama_embedding_adapter import OllamaEmbeddingAdapter
from stock.adapter.outbound.exaone_sentiment_adapter import ExaoneSentimentAdapter
from stock.adapter.outbound.gateways.fundamental_storage_gateway import FundamentalStorageGateway
from stock.adapter.outbound.gateways.news_label_storage_gateway import NewsLabelStorageGateway
from stock.adapter.outbound.gateways.news_search_gateway import NewsSearchGateway
from stock.adapter.outbound.gateways.news_storage_gateway import NewsStorageGateway
from stock.adapter.outbound.gateways.price_bar_storage_gateway import PriceBarStorageGateway
from stock.adapter.outbound.gateways.stock_analysis_gateway import StockAnalysisGateway
from stock.adapter.outbound.pg.fundamental_pg_repository import FundamentalPgRepository
from stock.adapter.outbound.pg.news_label_pg_repository import NewsLabelPgRepository
from stock.adapter.outbound.pg.news_pg_repository import NewsPgRepository
from stock.adapter.outbound.pg.price_bar_pg_repository import PriceBarPgRepository
from stock.adapter.outbound.yfinance_market_data_adapter import YFinanceMarketDataAdapter
from stock.app.ports.input.stock_use_case import StockUseCase
from stock.app.use_cases.fundamental_interactor import FundamentalInteractor
from stock.app.use_cases.news_interactor import NewsInteractor
from stock.app.use_cases.news_label_interactor import NewsLabelInteractor
from stock.app.use_cases.price_bar_interactor import PriceBarInteractor
from stock.app.use_cases.stock_interactor import StockInteractor
from stock.domain.entities.analysis_config import AnalysisConfig
from stock.domain.services.outlook_predictor import OutlookPredictor


def get_stock_use_case(db: AsyncSession = Depends(get_db)) -> StockUseCase:
    return StockInteractor(
        market_data=YFinanceMarketDataAdapter(),
        sentiment=ExaoneSentimentAdapter(),
        predictor=OutlookPredictor(),
        config=AnalysisConfig.default(),
        news=NewsPgRepository(session=db),
    )


def get_stock_analysis_gateway(
    use_case: StockUseCase = Depends(get_stock_use_case),
) -> StockAnalysisPort:
    """허브 StockAnalysisPort 구현 프로바이더 — main.py가 dependency_overrides로 주입."""
    return StockAnalysisGateway(use_case=use_case)


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


def get_news_label_storage_gateway(db: AsyncSession = Depends(get_db)) -> NewsLabelStoragePort:
    """허브 NewsLabelStoragePort 구현 프로바이더 — main.py가 dependency_overrides로 주입."""
    return NewsLabelStorageGateway(
        use_case=NewsLabelInteractor(labels=NewsLabelPgRepository(session=db))
    )


def get_price_bar_storage_gateway(db: AsyncSession = Depends(get_db)) -> PriceBarStoragePort:
    """허브 PriceBarStoragePort 구현 프로바이더 — main.py가 dependency_overrides로 주입."""
    return PriceBarStorageGateway(
        use_case=PriceBarInteractor(bars=PriceBarPgRepository(session=db))
    )


def get_fundamental_storage_gateway(db: AsyncSession = Depends(get_db)) -> FundamentalStoragePort:
    """허브 FundamentalStoragePort 구현 프로바이더 — main.py가 dependency_overrides로 주입."""
    return FundamentalStorageGateway(
        use_case=FundamentalInteractor(fundamentals=FundamentalPgRepository(session=db))
    )
