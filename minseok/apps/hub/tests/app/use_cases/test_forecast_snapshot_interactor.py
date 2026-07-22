from hub.app.dtos.forecast_snapshot_dto import ForecastCaptureOutcome, ForecastScoreOutcome
from hub.app.use_cases.forecast_snapshot_interactor import ForecastSnapshotInteractor


class _StubPort:
    def __init__(self):
        self.capture_args = None
        self.score_calls = 0

    async def capture(self, tickers, horizons):
        self.capture_args = (tickers, horizons)
        return ForecastCaptureOutcome(captured=len(tickers) * len(horizons), skipped=[])

    async def score(self):
        self.score_calls += 1
        return ForecastScoreOutcome(scored=3, pending=1)

    async def accuracy_report(self, horizon, recent_limit):  # pragma: no cover - 미사용
        raise NotImplementedError


async def test_capture_normalizes_and_delegates():
    port = _StubPort()
    outcome = await ForecastSnapshotInteractor(snapshots=port).capture(
        tickers=[" AAPL ", "", "MSFT"], horizons=[20, 5, 5, -1]
    )
    assert port.capture_args == (["AAPL", "MSFT"], [5, 20])
    assert outcome.captured == 4


async def test_capture_empty_tickers_short_circuits():
    port = _StubPort()
    outcome = await ForecastSnapshotInteractor(snapshots=port).capture(tickers=["  "], horizons=[5])
    assert port.capture_args is None
    assert outcome.captured == 0 and outcome.skipped == []


async def test_score_delegates():
    port = _StubPort()
    outcome = await ForecastSnapshotInteractor(snapshots=port).score()
    assert port.score_calls == 1
    assert outcome.scored == 3 and outcome.pending == 1
