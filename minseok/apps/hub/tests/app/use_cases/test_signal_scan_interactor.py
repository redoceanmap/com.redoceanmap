from hub.app.dtos.stock_analysis_dto import StockAnalysisResult
from hub.app.ports.output.stock_analysis_port import StockAnalysisUnavailable
from hub.app.use_cases.signal_scan_interactor import SignalScanInteractor

_RESULT = StockAnalysisResult(
    symbol="005930", price=290000.0, direction="UP", confidence=0.5,
    sentiment=0.5, sentiment_label="긍정", rsi=45.0, ma20=1.0, ma50=1.0,
    support=1.0, resistance=2.0, headlines=[],
)


class _StubStocks:
    async def analyze(self, query):
        if query == "없는종목":
            raise StockAnalysisUnavailable("종목을 찾지 못했습니다: 없는종목")
        return _RESULT


async def test_스캔은_해석_실패_종목을_건너뛴다():
    results = await SignalScanInteractor(_StubStocks()).scan(["삼성전자", "없는종목", "AAPL"])
    assert len(results) == 2
    assert all(r.symbol == "005930" for r in results)
