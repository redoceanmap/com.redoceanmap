from __future__ import annotations

from dataclasses import dataclass

from hub.app.dtos.area_backtest_report_dto import AreaBacktestReportInfo
from hub.app.dtos.forecast_snapshot_dto import ForecastAccuracyReport


@dataclass(frozen=True)
class ForecastReportResponse:
    report: ForecastAccuracyReport


@dataclass(frozen=True)
class MarketBacktestResponse:
    report: AreaBacktestReportInfo | None  # 백테스트 실행 이력이 없으면 None
