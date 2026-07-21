from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Query

from stock.adapter.inbound.api.schemas.stock_forecast_schema import StockForecastResponse
from stock.app.dtos.stock_forecast_dto import ForecastQuery
from stock.app.exceptions import MarketDataUnavailableError
from stock.app.ports.input.stock_forecast_use_case import StockForecastUseCase
from stock.dependencies.stock_forecast_provider import get_stock_forecast_use_case

stock_forecast_router = APIRouter(prefix="/stock", tags=["stock"])


@stock_forecast_router.get("/{symbol}/forecast", response_model=StockForecastResponse)
async def get_stock_forecast(
    symbol: str,
    horizon: int = Query(default=5, ge=1, le=20),
    use_case: StockForecastUseCase = Depends(get_stock_forecast_use_case),
) -> StockForecastResponse:
    try:
        view = await use_case.forecast(ForecastQuery(symbol=symbol, horizon=horizon))
    except MarketDataUnavailableError as e:
        raise HTTPException(status_code=404, detail=e.detail)
    return StockForecastResponse(**asdict(view))
