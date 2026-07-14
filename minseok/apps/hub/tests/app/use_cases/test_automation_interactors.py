from datetime import datetime, timezone

from hub.app.dtos.news_dto import NewsItem
from hub.app.dtos.price_bar_dto import PriceBarItem
from hub.app.dtos.stock_analysis_dto import StockAnalysisResult
from hub.app.ports.output.stock_analysis_port import StockAnalysisUnavailable
from hub.app.use_cases.news_ingest_interactor import NewsIngestInteractor
from hub.app.use_cases.price_bar_ingest_interactor import PriceBarIngestInteractor
from hub.app.use_cases.signal_scan_interactor import SignalScanInteractor

_RESULT = StockAnalysisResult(
    symbol="005930", price=290000.0, direction="UP", confidence=0.5,
    sentiment=0.5, sentiment_label="긍정", rsi=45.0, ma20=1.0, ma50=1.0,
    support=1.0, resistance=2.0, headlines=[],
)


class _StubStorage:
    def __init__(self):
        self.saved: list[NewsItem] = []

    async def save_many(self, items):
        self.saved.extend(items)
        return len(items)


class _StubStocks:
    async def analyze(self, query):
        if query == "없는종목":
            raise StockAnalysisUnavailable("종목을 찾지 못했습니다: 없는종목")
        return _RESULT


async def test_뉴스_적재는_빈_항목을_거른다():
    storage = _StubStorage()
    saved = await NewsIngestInteractor(storage).ingest([
        NewsItem(title="삼성전자 실적 발표", source="test", url="https://a"),
        NewsItem(title="  ", source="test", url="https://b"),
        NewsItem(title="제목만", source="test", url=""),
    ])
    assert saved == 1
    assert [i.url for i in storage.saved] == ["https://a"]


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


async def test_스캔은_해석_실패_종목을_건너뛴다():
    results = await SignalScanInteractor(_StubStocks()).scan(["삼성전자", "없는종목", "AAPL"])
    assert len(results) == 2
    assert all(r.symbol == "005930" for r in results)
