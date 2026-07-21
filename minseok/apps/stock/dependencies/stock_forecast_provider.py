from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from stock.adapter.outbound.pg.forecast_history_pg_repository import ForecastHistoryPgRepository
from stock.adapter.outbound.yfinance_market_data_adapter import YFinanceMarketDataAdapter
from stock.app.ports.input.stock_forecast_use_case import StockForecastUseCase
from stock.app.use_cases.stock_forecast_interactor import StockForecastInteractor


def get_stock_forecast_use_case(db: AsyncSession = Depends(get_db)) -> StockForecastUseCase:
    return StockForecastInteractor(
        history=ForecastHistoryPgRepository(session=db),
        market_data=YFinanceMarketDataAdapter(),  # 미수집 종목 라이브 폴백
    )
