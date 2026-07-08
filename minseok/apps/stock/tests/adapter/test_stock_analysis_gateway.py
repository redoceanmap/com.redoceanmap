import pytest

from hub.app.ports.output.stock_analysis_port import StockAnalysisUnavailable
from stock.adapter.outbound.gateways import stock_analysis_gateway as gw_module
from stock.adapter.outbound.gateways.stock_analysis_gateway import StockAnalysisGateway
from stock.app.dtos.stock_analysis_dto import StockAnalysis
from stock.app.exceptions import MarketDataUnavailableError

_ANALYSIS = StockAnalysis(
    symbol="005930", price=290250.0, direction="UP", confidence=0.55,
    sentiment=0.7, sentiment_label="긍정", rsi=43.3, ma20=328862.5, ma50=294535.0,
    support=190100.0, resistance=374500.0, headlines=["헤드라인"],
)


class _StubUseCase:
    async def analyze(self, symbol, name=None):
        assert symbol.code == "005930"
        assert name == "삼성전자"  # 원 질의가 뉴스 검색용으로 전달된다
        return _ANALYSIS


class _FailingUseCase:
    async def analyze(self, symbol, name=None):
        raise MarketDataUnavailableError("시세 데이터를 찾지 못했습니다: X")


async def test_질의를_해석해_허브_DTO로_변환(monkeypatch):
    async def fake_resolve(query):
        assert query == "삼성전자"
        return "005930"

    monkeypatch.setattr(gw_module, "resolve_symbol", fake_resolve)
    result = await StockAnalysisGateway(use_case=_StubUseCase()).analyze("삼성전자")
    assert result.symbol == "005930"
    assert result.direction == "UP"
    assert result.support == 190100.0
    assert result.headlines == ["헤드라인"]


async def test_앱_예외는_허브_계약_예외로_변환(monkeypatch):
    async def fake_resolve(query):
        return "005930"

    monkeypatch.setattr(gw_module, "resolve_symbol", fake_resolve)
    with pytest.raises(StockAnalysisUnavailable):
        await StockAnalysisGateway(use_case=_FailingUseCase()).analyze("삼성전자")
