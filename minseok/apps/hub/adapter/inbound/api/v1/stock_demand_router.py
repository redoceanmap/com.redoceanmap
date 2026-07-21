"""stock_demand_router.py — 워치리스트 수요 편입 스크립트의 수요 조회 창구."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from hub.adapter.inbound.api.schemas.stock_demand_schema import StockDemandSchema
from hub.adapter.inbound.api.v1.webhook_token import verify_webhook_token
from hub.app.ports.input.stock_demand_use_case import StockDemandUseCase
from hub.dependencies.stock_demand_provider import get_stock_demand_use_case

stock_demand_router = APIRouter(
    prefix="/automation", tags=["automation"],
    dependencies=[Depends(verify_webhook_token)],
)


@stock_demand_router.get(
    "/stock-demand", response_model=list[StockDemandSchema],
    summary="분석 질문 수요 상위 — 워치리스트 수요 편입 판단용",
)
async def top_stock_demands(
    days: int = Query(default=14, ge=1, le=90),
    limit: int = Query(default=10, ge=1, le=50),
    use_case: StockDemandUseCase = Depends(get_stock_demand_use_case),
) -> list[StockDemandSchema]:
    return [
        StockDemandSchema(ticker=r.ticker, ask_count=r.ask_count, last_asked_at=r.last_asked_at)
        for r in await use_case.top_demands(days=days, limit=limit)
    ]
