"""price_bar_ingest_router.py — 수집기(cron)의 OHLCV 봉 적재·커버리지 창구."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from hub.adapter.inbound.api.schemas.price_bar_ingest_schema import (
    PriceBarIngestRequest,
    PriceBarIngestResult,
    PriceCoverageSchema,
)
from hub.adapter.inbound.api.v1.webhook_token import verify_webhook_token
from hub.app.dtos.price_bar_dto import PriceBarItem
from hub.app.ports.input.price_bar_ingest_use_case import PriceBarIngestUseCase
from hub.dependencies.price_bar_ingest_provider import get_price_bar_ingest_use_case

price_bar_ingest_router = APIRouter(
    prefix="/automation", tags=["automation"],
    dependencies=[Depends(verify_webhook_token)],
)


@price_bar_ingest_router.post(
    "/prices", response_model=PriceBarIngestResult, summary="수집기 OHLCV 봉 적재",
)
async def ingest_prices(
    payload: PriceBarIngestRequest,
    use_case: PriceBarIngestUseCase = Depends(get_price_bar_ingest_use_case),
) -> PriceBarIngestResult:
    saved = await use_case.ingest([
        PriceBarItem(
            ticker=i.ticker, timeframe=i.timeframe, ts=i.ts,
            open=i.open, high=i.high, low=i.low, close=i.close, volume=i.volume,
        )
        for i in payload.items
    ])
    return PriceBarIngestResult(received=len(payload.items), saved=saved)


@price_bar_ingest_router.get(
    "/prices/coverage", response_model=list[PriceCoverageSchema],
    summary="(ticker, timeframe)별 보유 구간 — 수집기의 백필 깊이 판단용",
)
async def price_coverage(
    use_case: PriceBarIngestUseCase = Depends(get_price_bar_ingest_use_case),
) -> list[PriceCoverageSchema]:
    return [
        PriceCoverageSchema(
            ticker=c.ticker, timeframe=c.timeframe,
            firstTs=c.first_ts, lastTs=c.last_ts, bars=c.bars,
        )
        for c in await use_case.coverage()
    ]
