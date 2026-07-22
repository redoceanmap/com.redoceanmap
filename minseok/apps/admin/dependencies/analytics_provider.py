from __future__ import annotations

from fastapi import Depends

from admin.app.ports.input.analytics_use_case import AnalyticsUseCase
from admin.app.use_cases.analytics_interactor import AnalyticsInteractor
from hub.app.ports.output.area_backtest_report_port import AreaBacktestReportPort
from hub.app.ports.output.forecast_snapshot_port import ForecastSnapshotPort
from hub.dependencies.area_backtest_report_provider import get_area_backtest_report_port
from hub.dependencies.forecast_snapshot_provider import get_forecast_snapshot_port


def get_analytics_use_case(
    forecasts: ForecastSnapshotPort = Depends(get_forecast_snapshot_port),
    area_backtests: AreaBacktestReportPort = Depends(get_area_backtest_report_port),
) -> AnalyticsUseCase:
    return AnalyticsInteractor(forecasts=forecasts, area_backtests=area_backtests)
