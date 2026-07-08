import pytest

from stock.domain.entities.outlook import Direction, Outlook
from stock.domain.services.backtester import Backtester


class _FixedPredictor:
    """항상 같은 방향을 내는 스텁 — 채점(회계) 로직만 검증한다."""

    def __init__(self, direction: Direction) -> None:
        self._direction = direction

    def predict(self, indicators, sentiment, config) -> Outlook:
        return Outlook(direction=self._direction, confidence=1.0)


def _series(values: list[float]) -> tuple[list[float], list[float], list[float]]:
    return values, [v - 1.0 for v in values], [v + 1.0 for v in values]


RISING = [float(100 + i) for i in range(100)]


def test_상승장에서_항상_UP이면_전부_적중():
    closes, lows, highs = _series(RISING)
    report = Backtester(predictor=_FixedPredictor(Direction.UP)).run(closes, lows, highs, horizon=5)
    assert report.up_signals == report.evaluated
    assert report.hit_rate == 1.0
    assert report.baseline_up_rate == 1.0


def test_상승장에서_항상_DOWN이면_전부_빗나감():
    closes, lows, highs = _series(RISING)
    report = Backtester(predictor=_FixedPredictor(Direction.DOWN)).run(closes, lows, highs, horizon=5)
    assert report.down_signals == report.evaluated
    assert report.hit_rate == 0.0


def test_신호_합계는_평가일수와_일치():
    closes, lows, highs = _series(RISING)
    report = Backtester().run(closes, lows, highs, horizon=5)
    assert report.up_signals + report.down_signals + report.neutral_signals == report.evaluated
    assert report.evaluated == len(closes) - 5 - 51


def test_횡보장은_실제_예측기로_전부_중립():
    closes, lows, highs = _series([100.0] * 100)
    report = Backtester().run(closes, lows, highs, horizon=5)
    assert report.neutral_signals == report.evaluated
    assert report.hit_rate is None


def test_데이터_부족이면_ValueError():
    closes, lows, highs = _series([100.0] * 50)
    with pytest.raises(ValueError):
        Backtester().run(closes, lows, highs, horizon=5)
