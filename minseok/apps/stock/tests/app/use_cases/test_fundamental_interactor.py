from datetime import date

from stock.app.use_cases.fundamental_interactor import FundamentalInteractor
from stock.domain.entities.fundamental_snapshot import FundamentalSnapshot


class _StubRepository:
    def __init__(self):
        self.saved: list[FundamentalSnapshot] = []

    async def save_many(self, snapshots):
        self.saved.extend(snapshots)
        return len(snapshots)


async def test_적재는_저장_신규_건수를_반환한다():
    repo = _StubRepository()
    snapshots = [
        FundamentalSnapshot(ticker="AAPL", as_of=date(2026, 7, 14), source="yfinance", per=38.4),
        FundamentalSnapshot(ticker="005930.KS", as_of=date(2026, 7, 14), source="dart", eps=4500.0),
    ]
    saved = await FundamentalInteractor(fundamentals=repo).ingest(snapshots)
    assert saved == 2
    assert [s.ticker for s in repo.saved] == ["AAPL", "005930.KS"]
