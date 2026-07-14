from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AreaStatsQuery:
    """상권 통계 조회 입력 — service_code 생략 시 최신 분기 매출 최대 업종을 자동 선택한다."""

    trdar_code: int
    service_code: str | None = None
    quarters: int = 4


@dataclass(frozen=True)
class AreaHeader:
    trdar_code: int
    trdar_name: str
    district_name: str


@dataclass(frozen=True)
class ServiceRef:
    code: str
    name: str


@dataclass(frozen=True)
class SalesQuarter:
    year_quarter: int
    monthly_sales_amount: int
    weekday_sales_amount: int


@dataclass(frozen=True)
class StoreQuarter:
    year_quarter: int
    store_count: int
    opening_rate: float
    closure_rate: float
    franchise_store_count: int


@dataclass(frozen=True)
class FloatingQuarter:
    year_quarter: int
    total: int
    age_10: int
    age_20: int
    age_30: int
    age_40: int
    age_50: int
    age_60_plus: int
    time_00_06: int
    time_06_11: int
    time_11_14: int
    time_14_17: int
    time_17_21: int
    time_21_24: int


@dataclass(frozen=True)
class ChangeSummary:
    change_indicator_name: str | None
    operating_months_avg: float | None
    region_operating_months_avg: float | None


@dataclass(frozen=True)
class QuarterStat:
    """분기 1개의 병합 통계 — 팩트별 결측은 None(적재 공백 허용)."""

    year_quarter: int
    monthly_sales: int | None = None
    weekday_sales: int | None = None
    store_count: int | None = None
    opening_rate: float | None = None
    closure_rate: float | None = None
    franchise_count: int | None = None
    total_floating_pop: int | None = None


@dataclass(frozen=True)
class AreaStatsView:
    trdar_code: int
    trdar_name: str
    district_name: str
    service_code: str | None  # 매출/점포 팩트가 전혀 없는 상권이면 None
    service_name: str | None
    series: list[QuarterStat]  # year_quarter 오름차순
    latest_floating: FloatingQuarter | None
    change: ChangeSummary | None
