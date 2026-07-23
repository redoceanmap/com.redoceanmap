from datetime import UTC, datetime

import pytest

from stock.app.dtos.stock_board_dto import BoardQuery, BoardSignalRow
from stock.app.ports.output.stock_board_repository import StockBoardRepositoryPort
from stock.app.ports.output.symbol_directory_port import SymbolDirectoryPort
from stock.app.use_cases.stock_board_interactor import StockBoardInteractor

AS_OF = datetime(2026, 7, 22, tzinfo=UTC)


def _row(ticker: str, direction: str, score: float, **kwargs) -> BoardSignalRow:
    defaults = dict(
        as_of=AS_OF,
        base_price=100.0,
        up_rate=None,
        baseline_up_rate=None,
        ready=False,
        closes=(98.0, 100.0),
    )
    defaults.update(kwargs)
    return BoardSignalRow(ticker=ticker, direction=direction, score=score, **defaults)


class _StubRepository(StockBoardRepositoryPort):
    def __init__(self, rows: list[BoardSignalRow]) -> None:
        self.rows = rows
        self.calls: list[tuple[int, int]] = []

    async def find_latest_signals(self, horizon: int, sparkline_bars: int):
        self.calls.append((horizon, sparkline_bars))
        return self.rows


class _StubDirectory(SymbolDirectoryPort):
    def display_name(self, ticker: str) -> str:
        return {"NVDA": "엔비디아"}.get(ticker, ticker)


def _interactor(rows: list[BoardSignalRow]) -> tuple[StockBoardInteractor, _StubRepository]:
    repo = _StubRepository(rows)
    return StockBoardInteractor(repository=repo, directory=_StubDirectory()), repo


async def test_신호가_뚜렷한_순서로_줄세운다():
    interactor, _ = _interactor([
        _row("AAA", "UP", 0.10),
        _row("BBB", "DOWN", -0.55),
        _row("CCC", "UP", 0.40),
    ])
    view = await interactor.board(BoardQuery(horizon=5, limit=10))
    assert [r.ticker for r in view.rows] == ["BBB", "CCC", "AAA"]  # |score| 내림차순


async def test_중립은_점수가_높아도_뒤로_민다():
    interactor, _ = _interactor([
        _row("NEU", "NEUTRAL", 0.90),
        _row("UPP", "UP", 0.10),
    ])
    view = await interactor.board(BoardQuery(horizon=5, limit=10))
    assert [r.ticker for r in view.rows] == ["UPP", "NEU"]


async def test_limit_만큼만_돌려준다():
    interactor, _ = _interactor([_row(f"T{i}", "UP", 0.5 - i * 0.01) for i in range(10)])
    view = await interactor.board(BoardQuery(horizon=5, limit=3))
    assert len(view.rows) == 3
    assert view.horizon_days == 5


async def test_이름과_전일_대비를_채운다():
    interactor, _ = _interactor([_row("NVDA", "UP", 0.5, closes=(200.0, 210.0))])
    row = (await interactor.board(BoardQuery(horizon=5, limit=10))).rows[0]
    assert row.name == "엔비디아"
    assert row.price == 210.0  # 스냅샷 base_price가 아니라 마지막 봉
    assert row.change_pct == pytest.approx(0.05)


async def test_봉이_한_개면_전일_대비는_None이다():
    interactor, _ = _interactor([_row("AAA", "UP", 0.5, closes=(210.0,))])
    row = (await interactor.board(BoardQuery(horizon=5, limit=10))).rows[0]
    assert row.change_pct is None
    assert row.price == 210.0


async def test_봉이_없으면_base_price로_열화한다():
    interactor, _ = _interactor([_row("AAA", "UP", 0.5, base_price=123.0, closes=())])
    row = (await interactor.board(BoardQuery(horizon=5, limit=10))).rows[0]
    assert row.price == 123.0
    assert row.change_pct is None


async def test_확률과_기준선이_모두_있을_때만_edge를_낸다():
    interactor, _ = _interactor([
        _row("AAA", "UP", 0.5, up_rate=0.58, baseline_up_rate=0.55),
        _row("BBB", "DOWN", -0.6, up_rate=0.40, baseline_up_rate=None),
    ])
    rows = {r.ticker: r for r in (await interactor.board(BoardQuery(horizon=5, limit=10))).rows}
    assert rows["AAA"].edge_pct == pytest.approx(0.03)
    assert rows["BBB"].edge_pct is None


async def test_horizon을_리포지토리에_그대로_넘긴다():
    interactor, repo = _interactor([])
    await interactor.board(BoardQuery(horizon=20, limit=5))
    assert repo.calls == [(20, 30)]  # SPARKLINE_BARS
