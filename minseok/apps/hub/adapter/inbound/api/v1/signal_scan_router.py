"""signal_scan_router.py — 외부 자동화(n8n)의 관심 종목 일괄 스캔 창구."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from hub.adapter.inbound.api.schemas.signal_scan_schema import (
    StockScanRequest,
    StockSignalSchema,
)
from hub.adapter.inbound.api.v1.webhook_token import verify_webhook_token
from hub.app.ports.input.signal_scan_use_case import SignalScanUseCase
from hub.dependencies.signal_scan_provider import get_signal_scan_use_case

signal_scan_router = APIRouter(
    prefix="/automation", tags=["automation"],
    dependencies=[Depends(verify_webhook_token)],
)


@signal_scan_router.post(
    "/stock-scan", response_model=list[StockSignalSchema], summary="관심 종목 일괄 스캔",
)
async def scan_stocks(
    payload: StockScanRequest,
    use_case: SignalScanUseCase = Depends(get_signal_scan_use_case),
) -> list[StockSignalSchema]:
    results = await use_case.scan(payload.symbols)
    return [
        StockSignalSchema(
            symbol=r.symbol,
            price=r.price,
            direction=r.direction,
            confidence=r.confidence,
            rsi=r.rsi,
            support=r.support,
            resistance=r.resistance,
            sentimentLabel=r.sentiment_label,
        )
        for r in results
    ]
