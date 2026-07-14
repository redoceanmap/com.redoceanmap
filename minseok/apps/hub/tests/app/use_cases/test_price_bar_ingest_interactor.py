from datetime import datetime, timezone

from hub.app.dtos.price_bar_dto import PriceBarItem
from hub.app.use_cases.price_bar_ingest_interactor import PriceBarIngestInteractor


class _StubPriceStorage:
    def __init__(self):
        self.saved: list[PriceBarItem] = []

    async def save_many(self, items):
        self.saved.extend(items)
        return len(items)

    async def coverage(self):
        return []


def _bar(**overrides):
    base = dict(
        ticker="NVDA", timeframe="5m", ts=datetime(2026, 7, 13, 13, 30, tzinfo=timezone.utc),
        open=209.9, high=210.5, low=209.1, close=210.0, volume=1_000_000,
    )
    return PriceBarItem(**{**base, **overrides})


async def test_봉_적재는_무효_봉을_거른다():
    storage = _StubPriceStorage()
    saved = await PriceBarIngestInteractor(storage).ingest([
        _bar(),
        _bar(ticker="  "),          # 티커 없음
        _bar(high=1.0, low=2.0),    # 고가 < 저가
        _bar(high=0.0, low=0.0),    # 가격 0 — 결측 봉
    ])
    assert saved == 1
    assert [i.ticker for i in storage.saved] == ["NVDA"]
