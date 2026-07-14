from datetime import date, datetime, timezone

import pytest

from stock.app.dtos.stock_history_dto import (
    FundamentalsQuery,
    PriceHistoryQuery,
    StockNewsItem,
    StockNewsQuery,
)
from stock.app.exceptions import MarketDataUnavailableError
from stock.app.use_cases.stock_history_interactor import StockHistoryInteractor
from stock.domain.entities.fundamental_snapshot import FundamentalSnapshot
from stock.domain.entities.price_bar import PriceBar

_TS = datetime(2026, 7, 13, tzinfo=timezone.utc)


def _bar(ticker="005930.KS", ts=_TS):
    return PriceBar(
        ticker=ticker, timeframe="1d", ts=ts,
        open=71000.0, high=71500.0, low=70800.0, close=71200.0, volume=9_000_000,
    )


class _StubRepo:
    def __init__(self, bars=None, news=None, fundamentals=None):
        self.bars = bars or []
        self.news = news or []
        self.fundamentals = fundamentals or []
        self.calls: list[tuple] = []

    async def find_bars(self, symbol, timeframe, limit):
        self.calls.append(("bars", symbol, timeframe, limit))
        return self.bars

    async def find_news(self, symbol, limit):
        self.calls.append(("news", symbol, limit))
        return self.news

    async def find_latest_fundamentals(self, symbol):
        self.calls.append(("fundamentals", symbol))
        return self.fundamentals


async def test_가격_이력은_저장_티커를_resolved_ticker로_노출한다():
    repo = _StubRepo(bars=[_bar()])
    history = await StockHistoryInteractor(history=repo).price_history(
        PriceHistoryQuery(symbol="005930")
    )
    assert history.resolved_ticker == "005930.KS"
    assert history.symbol == "005930"
    assert history.bars[0].close == 71200.0


async def test_가격_이력은_봉이_없으면_MarketDataUnavailableError():
    with pytest.raises(MarketDataUnavailableError):
        await StockHistoryInteractor(history=_StubRepo()).price_history(
            PriceHistoryQuery(symbol="XXXXXX")
        )


async def test_심볼은_대문자로_정규화되어_저장소에_전달된다():
    repo = _StubRepo(bars=[_bar(ticker="AAPL")])
    await StockHistoryInteractor(history=repo).price_history(
        PriceHistoryQuery(symbol=" aapl ", timeframe="5m", limit=100)
    )
    assert repo.calls == [("bars", "AAPL", "5m", 100)]


async def test_뉴스는_저장소_결과를_그대로_반환한다():
    item = StockNewsItem(
        id=1, title="삼성전자 실적 발표", source="yna", url="https://example.com/1",
        published_at=_TS, sentiment=0.6, event_type="earnings", confidence=0.9,
    )
    repo = _StubRepo(news=[item])
    items = await StockHistoryInteractor(history=repo).news(
        StockNewsQuery(symbol="005930", limit=5)
    )
    assert items == [item]
    assert repo.calls == [("news", "005930", 5)]


async def test_펀더멘털은_없어도_빈_snapshots로_반환한다():
    view = await StockHistoryInteractor(history=_StubRepo()).fundamentals(
        FundamentalsQuery(symbol="AAPL")
    )
    assert view.symbol == "AAPL"
    assert view.snapshots == []


async def test_펀더멘털은_소스별_스냅샷을_전달한다():
    snap = FundamentalSnapshot(ticker="005930.KS", as_of=date(2026, 7, 13), source="dart", eps=4500.0)
    view = await StockHistoryInteractor(history=_StubRepo(fundamentals=[snap])).fundamentals(
        FundamentalsQuery(symbol="005930")
    )
    assert view.snapshots == [snap]
