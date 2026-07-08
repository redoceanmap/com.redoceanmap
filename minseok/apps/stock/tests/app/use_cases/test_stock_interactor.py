from stock.app.dtos.stock_analysis_dto import StockAnalysis
from stock.app.use_cases.stock_interactor import StockInteractor
from stock.domain.entities.analysis_config import AnalysisConfig
from stock.domain.services.outlook_predictor import OutlookPredictor
from stock.domain.value_objects.indicators import Indicators
from stock.domain.value_objects.market_values import Price, Symbol
from stock.domain.value_objects.sentiment_score import SentimentScore


class _StubMarketData:
    async def latest_price(self, symbol):
        return Price(225.0)

    async def indicators(self, symbol):
        return Indicators(rsi=58.0, ma20=222.0, ma50=210.0, support=205.0, resistance=235.0)

    async def recent_headlines(self, symbol):
        return ["strong earnings", "price target raised"]


class _StubSentiment:
    async def analyze(self, headlines):
        return SentimentScore(0.7)


async def test_analyze_returns_structured_analysis_without_trade_rec():
    interactor = StockInteractor(
        market_data=_StubMarketData(),
        sentiment=_StubSentiment(),
        predictor=OutlookPredictor(),
        config=AnalysisConfig.default(),
    )
    result = await interactor.analyze(Symbol("AAPL"))

    assert isinstance(result, StockAnalysis)
    assert result.symbol == "AAPL"
    assert result.direction in {"UP", "DOWN", "NEUTRAL"}
    assert result.support == 205.0 and result.resistance == 235.0
    assert result.headlines == ["strong earnings", "price target raised"]
    # 매매 추천이 아니라 방향 전망만 — 주문/수량 필드가 없다.
    assert not hasattr(result, "ordered")
