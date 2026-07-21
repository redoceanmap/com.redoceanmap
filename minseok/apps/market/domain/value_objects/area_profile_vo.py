from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SalesMix:
    """최신 분기 매출 구조 분해 — 금액은 원 단위. 키 순서는 노출 순서와 같다."""

    year_quarter: int
    weekday_amount: int
    weekend_amount: int
    by_day: dict[str, int]     # mon..sun
    by_time: dict[str, int]    # t00_06..t21_24
    by_gender: dict[str, int]  # male, female
    by_age: dict[str, int]     # age10..age60Plus
    monthly_count: int
    monthly_amount: int = 0    # 월 총매출 — 객단가 계산용(0이면 성별 합으로 폴백)


@dataclass(frozen=True)
class AgeBand:
    band: str  # "10".."60+"
    male: int
    female: int


@dataclass(frozen=True)
class ResidentProfile:
    year_quarter: int
    total: int
    by_age: list[AgeBand]
    total_households: int
    apartment_households: int


@dataclass(frozen=True)
class WorkingProfile:
    year_quarter: int
    total: int
    by_age: list[AgeBand]


@dataclass(frozen=True)
class ApartmentProfile:
    year_quarter: int
    complex_count: int
    avg_price: int  # 원
    avg_area: int   # ㎡


@dataclass(frozen=True)
class SpendingCategory:
    key: str
    label: str
    amount: float  # 원


@dataclass(frozen=True)
class SpendingProfile:
    year_quarter: int
    monthly_avg_income: float | None  # 원
    total_expenditure: float | None   # 원
    by_category: list[SpendingCategory]  # 금액 내림차순, 결측 제외
