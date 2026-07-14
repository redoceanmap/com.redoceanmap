from stock.domain.entities.analysis_config import AnalysisConfig
from stock.domain.entities.outlook import Direction
from stock.domain.services.outlook_predictor import OutlookPredictor
from stock.domain.value_objects.indicators import Indicators
from stock.domain.value_objects.sentiment_score import SentimentScore


def _ind(rsi: float = 50.0, ma20: float = 100.0, ma50: float = 100.0) -> Indicators:
    return Indicators(rsi=rsi, ma20=ma20, ma50=ma50, support=90.0, resistance=110.0)


def test_positive_sentiment_and_uptrend_predicts_up():
    out = OutlookPredictor().predict(
        _ind(rsi=55.0, ma20=110.0, ma50=100.0), SentimentScore(0.8), AnalysisConfig.default()
    )
    assert out.direction is Direction.UP
    assert 0.0 < out.confidence <= 1.0


def test_negative_sentiment_and_overbought_predicts_down():
    out = OutlookPredictor().predict(
        _ind(rsi=75.0), SentimentScore(-0.8), AnalysisConfig.default()
    )
    assert out.direction is Direction.DOWN


def test_flat_signals_predict_neutral():
    out = OutlookPredictor().predict(_ind(), SentimentScore(0.0), AnalysisConfig.default())
    assert out.direction is Direction.NEUTRAL


def test_기본_config는_신규_피처를_무시한다():  # 기존 동작 보존 (가중치 0)
    extreme = Indicators(
        rsi=50.0, ma20=100.0, ma50=100.0, support=90.0, resistance=110.0,
        bb_percent_b=0.0, obv_slope=1.0, momentum_12_1=1.0, volume_ratio=0.1,  # 신규 신호가 강해도
    )
    out = OutlookPredictor().predict(extreme, SentimentScore(0.0), AnalysisConfig.default())
    assert out.direction is Direction.NEUTRAL


def test_bb_가중치를_주면_하단_밴드에서_상승_신호():
    config = AnalysisConfig(up_threshold=0.3, down_threshold=-0.3, w_bb=0.5)
    ind = Indicators(
        rsi=50.0, ma20=100.0, ma50=100.0, support=90.0, resistance=110.0, bb_percent_b=0.0,
    )
    out = OutlookPredictor().predict(ind, SentimentScore(0.0), config)
    assert out.direction is Direction.UP


def test_obv_가중치를_주면_수급_순증에서_상승_신호():
    config = AnalysisConfig(up_threshold=0.3, down_threshold=-0.3, w_obv=0.5)
    ind = Indicators(
        rsi=50.0, ma20=100.0, ma50=100.0, support=90.0, resistance=110.0, obv_slope=1.0,
    )
    out = OutlookPredictor().predict(ind, SentimentScore(0.0), config)
    assert out.direction is Direction.UP


def test_momentum_가중치를_주면_강한_상승_모멘텀에서_상승_신호():
    config = AnalysisConfig(up_threshold=0.3, down_threshold=-0.3, w_momentum=0.5)
    ind = Indicators(
        rsi=50.0, ma20=100.0, ma50=100.0, support=90.0, resistance=110.0, momentum_12_1=1.0,
    )
    out = OutlookPredictor().predict(ind, SentimentScore(0.0), config)
    assert out.direction is Direction.UP


def test_volume_confirm_미달이면_방향_신호를_관망으로_강등():
    config = AnalysisConfig(up_threshold=0.3, down_threshold=-0.3, w_bb=1.0, volume_confirm=1.0)
    ind = Indicators(
        rsi=50.0, ma20=100.0, ma50=100.0, support=90.0, resistance=110.0,
        bb_percent_b=0.0, volume_ratio=0.5,  # 강한 UP 신호 + 거래량 평소의 절반
    )
    out = OutlookPredictor().predict(ind, SentimentScore(0.0), config)
    assert out.direction is Direction.NEUTRAL
    assert out.confidence == 0.0


def test_volume_confirm_충족이면_방향_유지():
    config = AnalysisConfig(up_threshold=0.3, down_threshold=-0.3, w_bb=1.0, volume_confirm=1.0)
    ind = Indicators(
        rsi=50.0, ma20=100.0, ma50=100.0, support=90.0, resistance=110.0,
        bb_percent_b=0.0, volume_ratio=1.2,
    )
    out = OutlookPredictor().predict(ind, SentimentScore(0.0), config)
    assert out.direction is Direction.UP


def test_rsi_bb_reference_config는_과매도_밴드하단에서_up():
    ind = Indicators(
        rsi=20.0, ma20=100.0, ma50=100.0, support=90.0, resistance=110.0, bb_percent_b=0.0,
    )
    out = OutlookPredictor().predict(ind, SentimentScore(0.0), AnalysisConfig.rsi_bb_reference())
    assert out.direction is Direction.UP


def test_atr_veto_초과_변동성이면_무조건_관망():
    config = AnalysisConfig(up_threshold=0.3, down_threshold=-0.3, atr_veto=0.03)
    ind = Indicators(
        rsi=10.0, ma20=120.0, ma50=100.0, support=90.0, resistance=110.0, atr_pct=0.08,
    )
    out = OutlookPredictor().predict(ind, SentimentScore(0.9), config)  # 강한 신호에도
    assert out.direction is Direction.NEUTRAL
    assert out.confidence == 0.0
