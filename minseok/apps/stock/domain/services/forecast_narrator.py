from __future__ import annotations

from stock.domain.value_objects.backtest_report import MIN_SIGNAL_SAMPLES
from stock.domain.value_objects.forecast_distribution import DirectionStats
from stock.domain.value_objects.insight_vo import Insight

QUANTILE_MIN_SAMPLES = 30  # 이 미만이면 분위수 밴드 대신 ATR 콘 폴백

_DIRECTION_LABELS = {"UP": "상승", "DOWN": "하락", "NEUTRAL": "중립(관망)"}


def narrate(
    direction: str,
    stats: DirectionStats,
    baseline_up_rate: float,
    horizon_days: int,
    ready: bool,
) -> list[Insight]:
    """확률·밴드의 근거를 초보자 문장으로 — 항상 '과거 통계' 한계를 병기한다."""
    insights: list[Insight] = []

    if stats.sample_size > 0:
        up_pct = round(stats.hits / stats.sample_size * 100)
        base_pct = round(baseline_up_rate * 100)
        if direction == "NEUTRAL":
            lead = "과거 이 종목이 지금처럼 뚜렷한 방향 신호가 없던(중립) 날들 기준 — "
        else:
            lead = f"과거 이 종목에 지금과 같은 {_DIRECTION_LABELS[direction]} 신호가 났을 때 — "
        compare = "높습니다" if up_pct > base_pct else ("낮습니다" if up_pct < base_pct else "같습니다")
        insights.append(Insight(
            key="probability", tone="neutral",
            text=(
                f"{lead}{stats.sample_size}회 중 {stats.hits}회({up_pct}%)가 "
                f"{horizon_days}거래일 뒤 상승 마감했습니다. 평소 상승률 {base_pct}%보다 {compare}. "
                "과거 통계이며 미래를 보장하지 않습니다."
            ),
        ))

    if not ready:
        if direction == "NEUTRAL":
            text = "중립 신호의 통계는 방향 예측이 아니라 참고용입니다."
        else:
            text = (
                f"표본 {stats.sample_size}회 — 통계적 확신 기준(표본 {MIN_SIGNAL_SAMPLES}회 이상 + "
                "신뢰구간이 평소 상승률과 뚜렷이 구분)을 충족하지 못해 참고용입니다."
            )
        insights.append(Insight(key="sample", tone="warning", text=text))

    if stats.sample_size < QUANTILE_MIN_SAMPLES:
        insights.append(Insight(
            key="band", tone="neutral",
            text="같은 신호 표본이 적어 예측 범위는 실적 분포 대신 변동성(ATR) 기반으로 그렸습니다.",
        ))
    elif stats.median is not None:
        insights.append(Insight(
            key="band", tone="neutral",
            text=(
                f"차트의 예측 범위는 같은 신호 {stats.sample_size}회의 {horizon_days}일 뒤 "
                f"실적 분포입니다 — 중앙값 {stats.median * 100:+.1f}%, "
                f"가운데 절반이 {stats.q25 * 100:+.1f}%~{stats.q75 * 100:+.1f}% 사이였습니다."
            ),
        ))

    insights.append(Insight(
        key="basis", tone="neutral",
        text="이 통계는 기술 지표 신호만으로 계산했습니다(뉴스 감성 미반영).",
    ))
    return insights
