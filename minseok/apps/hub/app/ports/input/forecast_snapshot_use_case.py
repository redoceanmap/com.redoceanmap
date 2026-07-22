from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.forecast_snapshot_dto import ForecastCaptureOutcome, ForecastScoreOutcome


class ForecastSnapshotIngestUseCase(ABC):
    """자동화(cron)의 예측 스냅샷 창구 — 캡처·채점 트리거."""

    @abstractmethod
    async def capture(self, tickers: list[str], horizons: list[int]) -> ForecastCaptureOutcome:
        ...

    @abstractmethod
    async def score(self) -> ForecastScoreOutcome:
        ...
