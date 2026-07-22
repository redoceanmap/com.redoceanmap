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


def test_확률_제시_판정은_표본과_신뢰구간_하한을_모두_요구한다():
    from stock.domain.value_objects.backtest_report import BacktestReport, wilson_lower_bound

    # 표본 부족(n<100): 적중률이 높아도 불인정
    small = BacktestReport(
        horizon_days=5, evaluated=200, up_signals=50, down_signals=0,
        neutral_signals=150, up_hits=45, down_hits=0, baseline_up_rate=0.55,
    )
    assert not small.up_probability_ready

    # 표본 충분 + 하한이 기준선 초과: 인정
    strong = BacktestReport(
        horizon_days=5, evaluated=1000, up_signals=300, down_signals=0,
        neutral_signals=700, up_hits=210, down_hits=0, baseline_up_rate=0.55,
    )
    assert wilson_lower_bound(210, 300) > 0.55
    assert strong.up_probability_ready

    # 표본 충분해도 기준선 언저리: 불인정
    marginal = BacktestReport(
        horizon_days=5, evaluated=1000, up_signals=300, down_signals=0,
        neutral_signals=700, up_hits=168, down_hits=0, baseline_up_rate=0.55,
    )
    assert not marginal.up_probability_ready


def test_리포트_병합은_카운트_합산_기준선은_가중평균():
    from stock.domain.value_objects.backtest_report import BacktestReport

    a = BacktestReport(
        horizon_days=5, evaluated=100, up_signals=10, down_signals=5,
        neutral_signals=85, up_hits=6, down_hits=2, baseline_up_rate=0.6,
    )
    b = BacktestReport(
        horizon_days=5, evaluated=300, up_signals=30, down_signals=15,
        neutral_signals=255, up_hits=18, down_hits=9, baseline_up_rate=0.5,
    )
    m = a.merged(b)
    assert m.evaluated == 400
    assert m.up_signals == 40 and m.down_signals == 20
    assert m.up_hits == 24 and m.down_hits == 11
    assert abs(m.baseline_up_rate - (0.6 * 100 + 0.5 * 300) / 400) < 1e-9


def test_distribution_레짐_분할_합계는_무조건부와_일치():
    closes, lows, highs = _series(RISING)
    # 평가 구간(51~94)을 반씩 다른 레짐으로 — 봉 배열과 같은 길이
    regimes = ["BULL" if i < 70 else "BEAR" for i in range(len(closes))]
    dist = Backtester(predictor=_FixedPredictor(Direction.UP)).distribution(
        closes, lows, highs, horizon=5, regimes=regimes
    )
    total_by_regime = sum(r.evaluated for r in dist.by_regime.values())
    assert total_by_regime == dist.evaluated
    assert set(dist.by_regime) == {"BULL", "BEAR"}
    # 레짐 슬라이스의 방향 표본 합 = 슬라이스 평가일 수
    for stats in dist.by_regime.values():
        assert sum(d.sample_size for d in stats.by_direction.values()) == stats.evaluated
    # 상승장이라 조건부 기준선도 1.0
    assert all(r.baseline_up_rate == 1.0 for r in dist.by_regime.values())


def test_distribution_레짐_None은_무조건부에만_반영():
    closes, lows, highs = _series(RISING)
    regimes: list[str | None] = [None] * len(closes)
    dist = Backtester(predictor=_FixedPredictor(Direction.UP)).distribution(
        closes, lows, highs, horizon=5, regimes=regimes
    )
    assert dist.by_regime == {}
    assert dist.evaluated == len(closes) - 5 - 51


def test_distribution_excluded는_평가에서_빠지고_vetoed로_센다():
    closes, lows, highs = _series(RISING)
    excluded = [False] * len(closes)
    excluded[60] = excluded[61] = True  # 평가 구간 내 2일 veto
    dist = Backtester(predictor=_FixedPredictor(Direction.UP)).distribution(
        closes, lows, highs, horizon=5, excluded=excluded
    )
    assert dist.vetoed == 2
    assert dist.evaluated == len(closes) - 5 - 51 - 2
    assert dist.by_direction["UP"].sample_size == dist.evaluated


def test_distribution_무인자_하위호환():
    closes, lows, highs = _series(RISING)
    dist = Backtester(predictor=_FixedPredictor(Direction.UP)).distribution(
        closes, lows, highs, horizon=5
    )
    assert dist.by_regime == {} and dist.vetoed == 0


def test_distribution_길이_불일치는_ValueError():
    closes, lows, highs = _series(RISING)
    with pytest.raises(ValueError):
        Backtester().distribution(closes, lows, highs, horizon=5, regimes=["BULL"])
    with pytest.raises(ValueError):
        Backtester().distribution(closes, lows, highs, horizon=5, excluded=[True])
