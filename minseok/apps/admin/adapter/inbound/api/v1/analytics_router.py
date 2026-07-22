from dataclasses import asdict

from fastapi import APIRouter, Depends, Query

from admin.adapter.inbound.api.schemas.analytics_schema import (
    ForecastReportSchema,
    MarketBacktestReportSchema,
    MarketBacktestResponseSchema,
)
from admin.app.ports.input.analytics_use_case import AnalyticsUseCase
from admin.dependencies.analytics_provider import get_analytics_use_case
from core.security import require_permission

analytics_router = APIRouter(prefix="/admin", tags=["admin"])


@analytics_router.get(
    "/forecasts",
    response_model=ForecastReportSchema,
    dependencies=[Depends(require_permission("analytics:read"))],
    summary="주식 예측 채점 현황 — 적중률 요약 + 최근 스냅샷",
)
async def forecast_report(
    horizon: int | None = Query(default=None, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    use_case: AnalyticsUseCase = Depends(get_analytics_use_case),
) -> ForecastReportSchema:
    result = await use_case.forecast_report(horizon=horizon, limit=limit)
    return ForecastReportSchema(**asdict(result.report))


@analytics_router.get(
    "/market-backtest",
    response_model=MarketBacktestResponseSchema,
    dependencies=[Depends(require_permission("analytics:read"))],
    summary="상권 점수 워크포워드 백테스트 — 최신 실행 리포트",
)
async def market_backtest_report(
    use_case: AnalyticsUseCase = Depends(get_analytics_use_case),
) -> MarketBacktestResponseSchema:
    result = await use_case.market_backtest_report()
    return MarketBacktestResponseSchema(
        report=MarketBacktestReportSchema(**asdict(result.report))
        if result.report is not None else None
    )
