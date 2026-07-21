from datetime import UTC, datetime

from hub.app.dtos.stock_demand_dto import StockDemandRow
from hub.app.use_cases.stock_demand_interactor import StockDemandInteractor


class _StubPort:
    def __init__(self, rows):
        self.rows = rows
        self.called_with: tuple | None = None

    async def top_demands(self, days, limit):
        self.called_with = (days, limit)
        return self.rows


async def test_수요_조회를_포트에_위임한다():
    row = StockDemandRow(ticker="RKLB", ask_count=3, last_asked_at=datetime.now(UTC))
    port = _StubPort([row])
    got = await StockDemandInteractor(demand=port).top_demands(days=14, limit=10)
    assert got == [row]
    assert port.called_with == (14, 10)


async def test_수요가_없으면_빈_리스트():
    got = await StockDemandInteractor(demand=_StubPort([])).top_demands(days=14, limit=10)
    assert got == []
