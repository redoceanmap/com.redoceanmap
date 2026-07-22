from __future__ import annotations

from abc import ABC, abstractmethod

from stock.app.dtos.forecast_snapshot_dto import (
    CaptureCommand,
    CaptureResult,
    ScoreResult,
    SnapshotSummaryView,
)


class ForecastSnapshotUseCase(ABC):
    """예측 스냅샷 유스케이스 — 캡처(영속화)·채점·요약 조회."""

    @abstractmethod
    async def capture(self, command: CaptureCommand) -> CaptureResult:
        """티커별 forecast + 신호 분해를 저장한다. 미수집·봉 부족 티커는 skipped."""
        ...

    @abstractmethod
    async def score(self) -> ScoreResult:
        """horizon이 도래한 미채점 스냅샷을 price_bars(1d) 실현가로 채점한다."""
        ...

    @abstractmethod
    async def summary(self, horizon: int | None, recent_limit: int) -> SnapshotSummaryView:
        """적중률 요약 + 최근 스냅샷 목록 — 어드민 화면 1회 호출용."""
        ...
