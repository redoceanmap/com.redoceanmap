import pytest

from stock.domain.services.indicator_calculator import IndicatorCalculator


def _series(values: list[float]) -> tuple[list[float], list[float], list[float]]:
    """종가 기준으로 저가(-1)·고가(+1)를 파생한 (closes, lows, highs)."""
    return values, [v - 1.0 for v in values], [v + 1.0 for v in values]


def test_연속_상승이면_rsi_100():
    closes, lows, highs = _series([float(100 + i) for i in range(60)])
    ind = IndicatorCalculator().compute(closes, lows, highs)
    assert ind.rsi == 100.0


def test_연속_하락이면_rsi_0():
    closes, lows, highs = _series([float(200 - i) for i in range(60)])
    ind = IndicatorCalculator().compute(closes, lows, highs)
    assert ind.rsi == 0.0


def test_횡보면_rsi_중립_50():
    closes, lows, highs = _series([100.0] * 60)
    ind = IndicatorCalculator().compute(closes, lows, highs)
    assert ind.rsi == 50.0


def test_이동평균은_마지막_n개_평균():
    closes, lows, highs = _series([float(100 + i) for i in range(60)])
    ind = IndicatorCalculator().compute(closes, lows, highs)
    assert ind.ma20 == pytest.approx(sum(closes[-20:]) / 20)
    assert ind.ma50 == pytest.approx(sum(closes[-50:]) / 50)


def test_지지_저항은_최근_윈도_저점_고점():
    closes, lows, highs = _series([float(100 + i) for i in range(60)])
    ind = IndicatorCalculator().compute(closes, lows, highs)
    assert ind.support == min(lows[-60:])
    assert ind.resistance == max(highs[-60:])


def test_데이터_부족이면_ValueError():
    closes, lows, highs = _series([100.0] * 30)
    with pytest.raises(ValueError):
        IndicatorCalculator().compute(closes, lows, highs)
