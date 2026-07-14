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


def test_변동성_없는_횡보면_atr_0에_수렴_bb는_중립():
    closes = [100.0] * 60
    ind = IndicatorCalculator().compute(closes, closes, closes)  # 고=저=종
    assert ind.atr_pct == 0.0
    assert ind.bb_percent_b == 0.5  # 표준편차 0 → 중립


def test_상단_돌파면_bb_percent_b가_1_근처_이상():
    closes, lows, highs = _series([100.0] * 55 + [100.0, 101.0, 103.0, 106.0, 112.0])
    ind = IndicatorCalculator().compute(closes, lows, highs)
    assert ind.bb_percent_b > 0.9


def test_거래량_급증이면_volume_ratio_1_초과():
    closes, lows, highs = _series([float(100 + i) for i in range(60)])
    volumes = [1000.0] * 55 + [3000.0] * 5  # 최근 5일 3배
    ind = IndicatorCalculator().compute(closes, lows, highs, volumes)
    assert ind.volume_ratio > 1.5


def test_연속_상승이면_obv_slope_양수_연속_하락이면_음수():
    up_closes, up_lows, up_highs = _series([float(100 + i) for i in range(60)])
    volumes = [1000.0] * 60
    up = IndicatorCalculator().compute(up_closes, up_lows, up_highs, volumes)
    assert up.obv_slope > 0.9  # 매일 +거래량 → 정규화 값 ≈ 1

    dn_closes, dn_lows, dn_highs = _series([float(200 - i) for i in range(60)])
    dn = IndicatorCalculator().compute(dn_closes, dn_lows, dn_highs, volumes)
    assert dn.obv_slope < -0.9


def test_volumes_없으면_거래량_지표는_중립값():
    closes, lows, highs = _series([float(100 + i) for i in range(60)])
    ind = IndicatorCalculator().compute(closes, lows, highs)
    assert ind.volume_ratio == 1.0
    assert ind.obv_slope == 0.0


def test_모멘텀_12_1은_1개월전_대비_12개월전_수익률():
    closes, lows, highs = _series([float(100 + i) for i in range(260)])
    ind = IndicatorCalculator().compute(closes, lows, highs)
    assert ind.momentum_12_1 == pytest.approx(closes[-22] / closes[-253] - 1.0)


def test_이력_253봉_미만이면_모멘텀_중립_0():
    closes, lows, highs = _series([float(100 + i) for i in range(252)])
    ind = IndicatorCalculator().compute(closes, lows, highs)
    assert ind.momentum_12_1 == 0.0
