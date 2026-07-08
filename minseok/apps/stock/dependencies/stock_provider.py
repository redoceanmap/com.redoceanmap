from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from hub.app.ports.output.news_storage_port import NewsStoragePort
from hub.app.ports.output.stock_analysis_port import StockAnalysisPort
from stock.adapter.outbound.exaone_sentiment_adapter import ExaoneSentimentAdapter
from stock.adapter.outbound.gateways.news_storage_gateway import NewsStorageGateway
from stock.adapter.outbound.gateways.stock_analysis_gateway import StockAnalysisGateway
from stock.adapter.outbound.pg.news_pg_repository import NewsPgRepository
from stock.adapter.outbound.yfinance_market_data_adapter import YFinanceMarketDataAdapter
from stock.app.ports.input.stock_use_case import StockUseCase
from stock.app.use_cases.news_interactor import NewsInteractor
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
    return NewsStorageGateway(use_case=NewsInteractor(news=NewsPgRepository(session=db)))
