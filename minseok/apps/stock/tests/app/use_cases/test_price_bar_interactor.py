from datetime import datetime, timezone

from stock.app.dtos.price_bar_dto import PriceBarCoverage
from stock.app.use_cases.price_bar_interactor import PriceBarInteractor
from stock.domain.entities.price_bar import PriceBar

_TS = datetime(2026, 7, 13, 13, 30, tzinfo=timezone.utc)


def _bar(ts=_TS):
    return PriceBar(
        ticker="NVDA", timeframe="5m", ts=ts,
        open=209.9, high=210.5, low=209.1, close=210.0, volume=1_000_000,
    )


class _StubRepo:
    def __init__(self):
        self.saved: list[PriceBar] = []

    async def save_many(self, bars):
        self.saved.extend(bars)
        return len(bars)

    async def coverage(self):
        return [PriceBarCoverage(ticker="NVDA", timeframe="5m", first_ts=_TS, last_ts=_TS, bars=1)]


async def test_적재는_저장_신규_건수를_반환한다():
    repo = _StubRepo()
    saved = await PriceBarInteractor(bars=repo).ingest([_bar()])
    assert saved == 1
    assert repo.saved[0].ticker == "NVDA"


async def test_커버리지는_저장소_요약을_그대로_반환한다():
    coverage = await PriceBarInteractor(bars=_StubRepo()).coverage()
    assert coverage[0].bars == 1
    assert coverage[0].timeframe == "5m"
