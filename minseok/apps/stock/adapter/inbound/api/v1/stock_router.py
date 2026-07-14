import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from stock.app.dtos.stock_analysis_dto import StockAnalysis
from stock.app.exceptions import MarketDataUnavailableError
from stock.app.ports.input.stock_use_case import StockUseCase
from stock.dependencies.stock_provider import get_stock_use_case
from stock.domain.value_objects.market_values import Symbol
from stock.adapter.inbound.api.schemas.analyst_schema import AnalystResponseSchema
from stock.adapter.inbound.api.schemas.stock_history_schema import (
    FundamentalSnapshotSchema,
    FundamentalsResponse,
    PriceBarSchema,
    PriceHistoryResponse,
    StockNewsItemSchema,
)
from stock.app.dtos.analyst_dto import AnalystQuery
from stock.app.dtos.stock_history_dto import (
    FundamentalsQuery,
    PriceHistoryQuery,
    StockNewsQuery,
)
from stock.app.ports.input.analyst_use_case import AnalystUseCase
from stock.app.ports.input.stock_history_use_case import StockHistoryUseCase
from stock.dependencies.analyst_provider import get_analyst_use_case
from stock.dependencies.stock_history_provider import get_stock_history_use_case

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


@stock_router.get("/{symbol}/prices", response_model=PriceHistoryResponse)
async def get_price_history(
    symbol: str,
    timeframe: Literal["1d", "5m"] = "1d",
    limit: int = Query(default=500, ge=1, le=5000),
    use_case: StockHistoryUseCase = Depends(get_stock_history_use_case),
) -> PriceHistoryResponse:
    try:
        history = await use_case.price_history(
            PriceHistoryQuery(symbol=symbol, timeframe=timeframe, limit=limit)
        )
    except MarketDataUnavailableError as e:
        raise HTTPException(status_code=404, detail=e.detail)
    return PriceHistoryResponse(
        symbol=history.symbol,
        resolvedTicker=history.resolved_ticker,
        timeframe=history.timeframe,
        bars=[
            PriceBarSchema(
                ts=b.ts, open=b.open, high=b.high, low=b.low, close=b.close, volume=b.volume
            )
            for b in history.bars
        ],
    )


@stock_router.get("/{symbol}/news", response_model=list[StockNewsItemSchema])
async def get_stock_news(
    symbol: str,
    limit: int = Query(default=20, ge=1, le=100),
    use_case: StockHistoryUseCase = Depends(get_stock_history_use_case),
) -> list[StockNewsItemSchema]:
    items = await use_case.news(StockNewsQuery(symbol=symbol, limit=limit))
    return [
        StockNewsItemSchema(
            id=i.id, title=i.title, source=i.source, url=i.url,
            publishedAt=i.published_at,
            sentiment=i.sentiment, eventType=i.event_type, confidence=i.confidence,
        )
        for i in items
    ]


@stock_router.get("/{symbol}/fundamentals", response_model=FundamentalsResponse)
async def get_fundamentals(
    symbol: str,
    use_case: StockHistoryUseCase = Depends(get_stock_history_use_case),
) -> FundamentalsResponse:
    view = await use_case.fundamentals(FundamentalsQuery(symbol=symbol))
    return FundamentalsResponse(
        symbol=view.symbol,
        snapshots=[
            FundamentalSnapshotSchema(
                asOf=s.as_of, source=s.source, per=s.per, pbr=s.pbr, roe=s.roe,
                debtToEquity=s.debt_to_equity, fcf=s.fcf, marketCap=s.market_cap,
                eps=s.eps, bps=s.bps,
            )
            for s in view.snapshots
        ],
    )


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
