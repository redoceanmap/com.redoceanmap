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
    # 신규 지표 노출 — 스텁 Indicators는 기본값이라 중립값 그대로 내려온다.
    assert result.atr_pct == 0.0 and result.bb_percent_b == 0.5
    assert result.volume_ratio == 1.0 and result.obv_slope == 0.0
    assert result.momentum_12_1 == 0.0
    assert result.reference_up_signal is False  # rsi 58·%B 0.5 — 참고 신호 조건 미달
    # 매매 추천이 아니라 방향 전망만 — 주문/수량 필드가 없다.
    assert not hasattr(result, "ordered")


class _OversoldMarketData(_StubMarketData):
    async def indicators(self, symbol):
        # 과매도 + 밴드 하단 — 참고 신호(RSI+BB ±0.35) 발화 조건
        return Indicators(
            rsi=15.0, ma20=222.0, ma50=210.0, support=205.0, resistance=235.0, bb_percent_b=0.0,
        )


async def test_과매도_밴드하단이면_참고_신호가_켜진다():
    interactor = StockInteractor(
        market_data=_OversoldMarketData(),
        sentiment=_StubSentiment(),
        predictor=OutlookPredictor(),
        config=AnalysisConfig.default(),
    )
    result = await interactor.analyze(Symbol("AAPL"))

    assert result.reference_up_signal is True
    # 참고 신호는 본 판정(기본 config + 감성)을 오염시키지 않는다.
    assert result.direction in {"UP", "DOWN", "NEUTRAL"}
    assert result.sentiment == 0.7


class _StubDemand:
    def __init__(self, fail=False):
        self.fail = fail
        self.recorded: list[str] = []

    async def record(self, ticker):
        if self.fail:
            raise RuntimeError("DB down")
        self.recorded.append(ticker)


async def test_분석_시_수요를_기록한다():
    demand = _StubDemand()
    interactor = StockInteractor(
        market_data=_StubMarketData(),
        sentiment=_StubSentiment(),
        predictor=OutlookPredictor(),
        config=AnalysisConfig.default(),
        demand=demand,
    )
    await interactor.analyze(Symbol("AAPL"))
    assert demand.recorded == ["AAPL"]


async def test_수요_기록_실패는_분석에_영향_없다():
    interactor = StockInteractor(
        market_data=_StubMarketData(),
        sentiment=_StubSentiment(),
        predictor=OutlookPredictor(),
        config=AnalysisConfig.default(),
        demand=_StubDemand(fail=True),
    )
    result = await interactor.analyze(Symbol("AAPL"))
    assert result.price == 225.0  # 기록 실패에도 분석은 정상 반환
