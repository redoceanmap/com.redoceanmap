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
