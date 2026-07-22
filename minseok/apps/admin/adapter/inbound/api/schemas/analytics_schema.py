from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AccuracyKpiSchema(BaseModel):
    total: int
    scored: int
    pending: int
    hit_rate: float | None
    up_hit_rate: float | None
    down_hit_rate: float | None


class HorizonStatSchema(BaseModel):
    horizon_days: int
    scored: int
    hit_rate: float | None
    avg_realized_return_pct: float | None


class DirectionStatSchema(BaseModel):
    direction: str
    scored: int
    hit_rate: float | None
    avg_realized_return_pct: float | None


class SignalStatSchema(BaseModel):
    key: str
    n: int
    hits: int
    hit_rate: float | None


class SnapshotRowSchema(BaseModel):
    ticker: str
    as_of: datetime
    horizon_days: int
    direction: str
    base_price: float
    score: float
    up_rate: float | None
    ready: bool
    evaluated_at: datetime | None
    realized_return_pct: float | None
    hit: bool | None


class ForecastReportSchema(BaseModel):
    kpi: AccuracyKpiSchema
    by_horizon: list[HorizonStatSchema]
    by_direction: list[DirectionStatSchema]
    by_signal: list[SignalStatSchema]
    recent: list[SnapshotRowSchema]


class GradeOutcomeRowSchema(BaseModel):
    grade: str
    n: int
    avg_rel_floating_qoq: float | None
    median_rel_floating_qoq: float | None
    positive_share: float | None
    avg_sales_qoq: float | None
    sales_n: int


class ComponentRowSchema(BaseModel):
    key: str
    n: int
    spearman: float | None
    top_minus_bottom_quintile: float | None


class MarketBacktestReportSchema(BaseModel):
    ran_at: datetime
    params: dict
    n_observations: int
    n_areas: int
    base_quarters: list[int]
    grade_outcomes: list[GradeOutcomeRowSchema]
    component_predictiveness: list[ComponentRowSchema]


class MarketBacktestResponseSchema(BaseModel):
    report: MarketBacktestReportSchema | None
