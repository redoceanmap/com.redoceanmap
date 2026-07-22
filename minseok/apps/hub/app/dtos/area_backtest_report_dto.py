from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class GradeOutcomeRow:
    """등급별 다음 분기 실제 결과 — 등급이 미래를 갈랐는지의 실측."""

    grade: str                          # 우수 / 양호 / 보통 / 주의 / 위험
    n: int
    avg_rel_floating_qoq: float | None      # t+1 상대 유동인구 QoQ(%p, 상권−서울) 평균
    median_rel_floating_qoq: float | None
    positive_share: float | None            # 결과가 양(+)인 비율
    avg_sales_qoq: float | None             # t+1 매출 QoQ(%) 평균 — 2025 쌍만(저표본)
    sales_n: int


@dataclass(frozen=True)
class ComponentRow:
    """컴포넌트 점수(t)의 다음 분기 결과(t+1) 예측력."""

    key: str                               # sales_growth / floating_growth / store_health / persistence
    n: int
    spearman: float | None                 # 컴포넌트 점수 ↔ 결과의 순위 상관
    top_minus_bottom_quintile: float | None  # 상위 5분위 결과 평균 − 하위 5분위(%p)


@dataclass(frozen=True)
class AreaBacktestReportInfo:
    """상권 점수 워크포워드 백테스트 리포트 — 최신 실행 1건."""

    ran_at: datetime
    params: dict
    n_observations: int
    n_areas: int
    base_quarters: list[int]
    grade_outcomes: list[GradeOutcomeRow]
    component_predictiveness: list[ComponentRow]
