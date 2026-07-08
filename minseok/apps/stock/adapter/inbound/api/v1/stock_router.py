import logging

from fastapi import APIRouter, Depends, HTTPException

from stock.app.dtos.stock_analysis_dto import StockAnalysis
from stock.app.exceptions import MarketDataUnavailableError
from stock.app.ports.input.stock_use_case import StockUseCase
from stock.dependencies.stock_provider import get_stock_use_case
from stock.domain.value_objects.market_values import Symbol
from stock.adapter.inbound.api.schemas.analyst_schema import AnalystResponseSchema
from stock.app.dtos.analyst_dto import AnalystQuery
from stock.app.ports.input.analyst_use_case import AnalystUseCase
from stock.dependencies.analyst_provider import get_analyst_use_case

logger = logging.getLogger(__name__)

stock_router = APIRouter(prefix="/stock", tags=["stock"])


@stock_router.post("/analyze")
async def analyze(
    symbol: str = "AAPL",
    use_case: StockUseCase = Depends(get_stock_use_case),
) -> StockAnalysis:
    try:
        return await use_case.analyze(Symbol(code=symbol))
    except MarketDataUnavailableError as e:
        # 앱 계층 예외 → HTTP 변환은 인바운드 어댑터의 책임
        raise HTTPException(status_code=404, detail=e.detail)


@stock_router.get("/myself", response_model=AnalystResponseSchema)
async def introduce_myself(
    analyst: AnalystUseCase = Depends(get_analyst_use_case)
) -> AnalystResponseSchema:
    result = await analyst.introduce_myself(
        AnalystQuery(
            id=4,
            name="주식 분석 (stock)"
        )
    )
    return AnalystResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )
