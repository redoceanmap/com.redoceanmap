from __future__ import annotations

import logging

from hub.app.dtos.forecast_snapshot_dto import ForecastCaptureOutcome, ForecastScoreOutcome
from hub.app.ports.input.forecast_snapshot_use_case import ForecastSnapshotIngestUseCase
from hub.app.ports.output.forecast_snapshot_port import ForecastSnapshotPort

logger = logging.getLogger(__name__)

# 캡처 요청 상한 — 배치 실수로 전 티커·다중 horizon이 한 번에 몰리는 것을 막는다
MAX_TICKERS = 50
MAX_HORIZONS = 4


class ForecastSnapshotInteractor(ForecastSnapshotIngestUseCase):
    """예측 스냅샷 허브 대장 — 입력을 다듬어 스포크 구현(포트)에 위임한다."""

    def __init__(self, snapshots: ForecastSnapshotPort) -> None:
        self._snapshots = snapshots

    async def capture(self, tickers: list[str], horizons: list[int]) -> ForecastCaptureOutcome:
        valid_tickers = [t.strip() for t in tickers if t.strip()][:MAX_TICKERS]
        valid_horizons = sorted({h for h in horizons if h > 0})[:MAX_HORIZONS] or [5]
        if not valid_tickers:
            return ForecastCaptureOutcome(captured=0, skipped=[])
        outcome = await self._snapshots.capture(valid_tickers, valid_horizons)
        logger.info(
            "[hub-forecast-snapshot] %d티커×%s 캡처 %d건 skip %d",
            len(valid_tickers), valid_horizons, outcome.captured, len(outcome.skipped),
        )
        return outcome

    async def score(self) -> ForecastScoreOutcome:
        outcome = await self._snapshots.score()
        logger.info(
            "[hub-forecast-snapshot] 채점 %d건, 대기 %d건", outcome.scored, outcome.pending
        )
        return outcome
