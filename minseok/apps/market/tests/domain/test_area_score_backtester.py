import pytest

from market.domain.services.area_score_backtester import (
    AreaScoreBacktester,
    ScoredObservation,
)


def _obs(code: str, grade: str = "보통", total: float = 50.0,
         components: dict | None = None, outcome: float = 0.0,
         sales: float | None = None, quarter: int = 20241) -> ScoredObservation:
    return ScoredObservation(
        trdar_code=code, year_quarter=quarter, grade=grade, total=total,
        component_scores=components or {}, outcome_rel_floating_qoq=outcome,
        outcome_sales_qoq=sales,
    )


def test_aggregate_counts_and_quarters():
    obs = [
        _obs("A", quarter=20241), _obs("A", quarter=20242), _obs("B", quarter=20241),
    ]
    payload = AreaScoreBacktester().aggregate(obs)
    assert payload["n_observations"] == 3
    assert payload["n_areas"] == 2
    assert payload["base_quarters"] == [20241, 20242]


def test_grade_outcomes_aggregation():
    obs = [
        _obs("A", grade="우수", outcome=2.0, sales=1.0),
        _obs("B", grade="우수", outcome=-1.0),
        _obs("C", grade="위험", outcome=-3.0),
    ]
    rows = {r["grade"]: r for r in AreaScoreBacktester().aggregate(obs)["grade_outcomes"]}

    good = rows["우수"]
    assert good["n"] == 2
    assert good["avg_rel_floating_qoq"] == pytest.approx(0.5)
    assert good["median_rel_floating_qoq"] == pytest.approx(0.5)
    assert good["positive_share"] == pytest.approx(0.5)
    assert good["avg_sales_qoq"] == pytest.approx(1.0)  # sales 있는 관측만
    assert good["sales_n"] == 1

    empty = rows["양호"]  # 관측 없는 등급도 행은 나온다(표 고정)
    assert empty["n"] == 0 and empty["avg_rel_floating_qoq"] is None
    assert rows["위험"]["positive_share"] == 0.0


def test_spearman_perfect_correlations():
    bt = AreaScoreBacktester()
    assert bt._spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert bt._spearman([1, 2, 3, 4], [40, 30, 20, 10]) == pytest.approx(-1.0)


def test_spearman_ties_and_degenerate():
    bt = AreaScoreBacktester()
    # 동순위 평균 처리 — 예외 없이 -1~1 범위
    r = bt._spearman([1, 1, 2, 3], [5, 6, 7, 8])
    assert r is not None and -1.0 <= r <= 1.0
    assert bt._spearman([1, 2], [3, 4]) is None          # 표본 3 미만
    assert bt._spearman([5, 5, 5], [1, 2, 3]) is None    # 상수 시리즈


def test_component_predictiveness_uses_available_components_only():
    obs = [
        _obs("A", components={"floating_growth": 80.0, "persistence": 60.0}, outcome=2.0),
        _obs("B", components={"floating_growth": 40.0}, outcome=-1.0),
        _obs("C", components={"floating_growth": 60.0}, outcome=1.0),
    ]
    rows = {r["key"]: r for r in
            AreaScoreBacktester().aggregate(obs)["component_predictiveness"]}
    assert rows["floating_growth"]["n"] == 3
    assert rows["floating_growth"]["spearman"] == pytest.approx(1.0)
    assert rows["persistence"]["n"] == 1
    assert rows["persistence"]["spearman"] is None
    # 표본 25 미만 — 5분위 스프레드는 None
    assert rows["floating_growth"]["top_minus_bottom_quintile"] is None


def test_quintile_spread_with_enough_samples():
    # 점수와 결과가 완전 비례하는 관측 25건 → 상위-하위 5분위 스프레드 양수
    obs = [
        _obs(f"T{i}", components={"floating_growth": float(i)}, outcome=float(i))
        for i in range(25)
    ]
    rows = {r["key"]: r for r in
            AreaScoreBacktester().aggregate(obs)["component_predictiveness"]}
    spread = rows["floating_growth"]["top_minus_bottom_quintile"]
    # 하위 5개 평균 0..4=2, 상위 5개 평균 20..24=22 → 20
    assert spread == pytest.approx(20.0)


def test_aggregate_empty_observations():
    payload = AreaScoreBacktester().aggregate([])
    assert payload["n_observations"] == 0
    assert payload["component_predictiveness"] == []
    assert all(r["n"] == 0 for r in payload["grade_outcomes"])
