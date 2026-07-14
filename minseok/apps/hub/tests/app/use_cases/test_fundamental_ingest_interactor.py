from datetime import date

from hub.app.dtos.fundamental_dto import FundamentalSnapshotItem
from hub.app.use_cases.fundamental_ingest_interactor import FundamentalIngestInteractor


class _StubFundamentalStorage:
    def __init__(self):
        self.saved: list[FundamentalSnapshotItem] = []

    async def save_many(self, items):
        self.saved.extend(items)
        return len(items)


def _snapshot(**overrides):
    base = dict(ticker="AAPL", as_of=date(2026, 7, 14), source="yfinance", per=38.4, roe=1.41)
    return FundamentalSnapshotItem(**{**base, **overrides})


async def test_펀더멘털_적재는_무효_스냅샷을_거른다():
    storage = _StubFundamentalStorage()
    saved = await FundamentalIngestInteractor(storage).ingest([
        _snapshot(),
        _snapshot(ticker="  "),                  # 티커 없음
        _snapshot(ticker="MSFT", source=" "),    # 소스 없음
        _snapshot(ticker="NVDA", per=None, roe=None),  # 전 지표 결측
    ])
    assert saved == 1
    assert [i.ticker for i in storage.saved] == ["AAPL"]
