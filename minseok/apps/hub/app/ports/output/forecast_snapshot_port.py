from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.forecast_snapshot_dto import (
    ForecastAccuracyReport,
    ForecastCaptureOutcome,
    ForecastScoreOutcome,
)


class ForecastSnapshotPort(ABC):
    """허브가 스포크에 위임하는 예측 스냅샷 추상 — 캡처·채점·정확도 리포트.

    구현은 stock 게이트웨이. 자동화(cron)가 capture/score를 부르고,
    admin의 analytics 인터랙터가 accuracy_report를 소비한다
    (PriceBarStoragePort.coverage()를 admin이 같이 소비하는 선례와 동일).
    """

    @abstractmethod
    async def capture(self, tickers: list[str], horizons: list[int]) -> ForecastCaptureOutcome:
        """티커별 forecast 스냅샷을 저장한다. 중복(같은 봉)은 무시."""
        ...

    @abstractmethod
    async def score(self) -> ForecastScoreOutcome:
        """horizon이 도래한 미채점 스냅샷을 실현 수익률로 채점한다."""
        ...

    @abstractmethod
    async def accuracy_report(self, horizon: int | None, recent_limit: int) -> ForecastAccuracyReport:
        """적중률 요약 + 최근 스냅샷 — 어드민 화면 1회 호출용."""
        ...
