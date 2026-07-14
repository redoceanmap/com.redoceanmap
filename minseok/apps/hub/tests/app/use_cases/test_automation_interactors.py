from datetime import date, datetime, timezone

from hub.app.dtos.fundamental_dto import FundamentalSnapshotItem
from hub.app.dtos.news_dto import NewsItem
from hub.app.dtos.news_label_dto import NewsLabelItem
from hub.app.dtos.price_bar_dto import PriceBarItem
from hub.app.dtos.stock_analysis_dto import StockAnalysisResult
from hub.app.ports.output.stock_analysis_port import StockAnalysisUnavailable
from hub.app.use_cases.fundamental_ingest_interactor import FundamentalIngestInteractor
from hub.app.use_cases.news_ingest_interactor import NewsIngestInteractor
from hub.app.use_cases.news_label_ingest_interactor import NewsLabelIngestInteractor
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


class _StubLabelStorage:
    def __init__(self):
        self.saved: list[NewsLabelItem] = []

    async def save_many(self, items):
        self.saved.extend(items)
        return len(items)

    async def unlabeled(self, labeler, limit):
        return []


def _label(**overrides):
    base = dict(news_id=1, labeler="exaone-2.4b-awq", sentiment=0.7, event_type="실적", confidence=0.9)
    return NewsLabelItem(**{**base, **overrides})


async def test_라벨_적재는_범위_밖_라벨을_거른다():
    storage = _StubLabelStorage()
    saved = await NewsLabelIngestInteractor(storage).ingest([
        _label(),
        _label(news_id=2, sentiment=1.5),     # 감성 범위 밖
        _label(news_id=3, confidence=-0.1),   # 확신도 범위 밖
        _label(news_id=4, labeler=" "),       # 라벨러 없음
    ])
    assert saved == 1
    assert [i.news_id for i in storage.saved] == [1]


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


async def test_스캔은_해석_실패_종목을_건너뛴다():
    results = await SignalScanInteractor(_StubStocks()).scan(["삼성전자", "없는종목", "AAPL"])
    assert len(results) == 2
    assert all(r.symbol == "005930" for r in results)
