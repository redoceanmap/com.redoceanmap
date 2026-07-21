from __future__ import annotations

from market.domain.value_objects.area_profile_vo import (
    ResidentProfile,
    SalesMix,
    SpendingProfile,
    WorkingProfile,
)
from market.domain.value_objects.insight_vo import Insight

# 임계값 — 경계 동작은 테스트로 고정한다
WEEKEND_HIGH = 0.45   # 주말 비중 이 이상이면 나들이·외식형
WEEKEND_LOW = 0.15    # 주말 비중 이 이하면 평일 수요 중심
PEAK_TIME_MIN = 0.35  # 시간대 최대 비중 언급 기준
PEAK_DAY_MIN = 0.20   # 요일 최대 비중 병기 기준
GENDER_MIN = 0.60     # 우세 성별 언급 기준
AGE_MIN = 0.30        # 핵심 연령대 언급 기준
OFFICE_RATIO = 2.0    # 직장/상주 비 이 이상이면 오피스형
RESIDENT_RATIO = 0.5  # 직장/상주 비 이 이하면 주거형
APT_SHARE_MIN = 0.5   # 아파트 가구 비중 언급 기준

_TIME_LABELS = {
    "t00_06": "새벽(00~06시)",
    "t06_11": "오전(06~11시)",
    "t11_14": "점심(11~14시)",
    "t14_17": "오후(14~17시)",
    "t17_21": "저녁(17~21시)",
    "t21_24": "밤(21~24시)",
}
_DAY_LABELS = {
    "mon": "월요일", "tue": "화요일", "wed": "수요일", "thu": "목요일",
    "fri": "금요일", "sat": "토요일", "sun": "일요일",
}
_AGE_LABELS = {
    "age10": "10대", "age20": "20대", "age30": "30대",
    "age40": "40대", "age50": "50대", "age60Plus": "60대 이상",
}
_GENDER_LABELS = {"male": "남성", "female": "여성"}


def narrate(
    sales: SalesMix | None,
    resident: ResidentProfile | None,
    working: WorkingProfile | None,
    spending: SpendingProfile | None,
) -> list[Insight]:
    """최신 분기 구조 수치 → 초보자용 해석 문장. 결측 축은 해당 문장을 생략한다."""
    insights: list[Insight] = []
    if sales is not None:
        insights += _sales_insights(sales)
    insights += _demand_insights(resident, working)
    if spending is not None:
        insights += _spending_insights(spending)
    if sales is not None:
        ticket = _avg_ticket(sales)
        if ticket is not None:
            insights.append(ticket)
    return insights


def _sales_insights(sales: SalesMix) -> list[Insight]:
    out: list[Insight] = []
    total_wk = sales.weekday_amount + sales.weekend_amount
    if total_wk > 0:
        weekend_ratio = sales.weekend_amount / total_wk
        weekend_pct = round(weekend_ratio * 100)
        if weekend_ratio >= WEEKEND_HIGH:
            text = f"주말 매출 비중이 {weekend_pct}% — 나들이·외식 수요가 큰 상권입니다."
        elif weekend_ratio <= WEEKEND_LOW:
            text = f"주중 매출이 {100 - weekend_pct}% — 직장인 평일 수요 중심 상권입니다."
        else:
            text = f"주중 {100 - weekend_pct}%·주말 {weekend_pct}%로 매출이 고르게 분포합니다."
        out.append(Insight(key="sales_rhythm_weekend", tone="neutral", text=text))

    peak = _peak_text(sales)
    if peak is not None:
        out.append(peak)

    gender = _dominant(sales.by_gender)
    if gender is not None:
        key, ratio = gender
        if ratio >= GENDER_MIN:
            out.append(Insight(
                key="customer_gender", tone="neutral",
                text=f"{_GENDER_LABELS[key]} 고객 매출이 {round(ratio * 100)}% — "
                     f"{_GENDER_LABELS[key]} 고객 비중이 뚜렷한 상권입니다.",
            ))

    age = _dominant(sales.by_age)
    if age is not None:
        key, ratio = age
        if ratio >= AGE_MIN:
            out.append(Insight(
                key="customer_age", tone="neutral",
                text=f"{_AGE_LABELS[key]} 고객이 매출의 {round(ratio * 100)}%로 핵심 고객층입니다.",
            ))
    return out


def _peak_text(sales: SalesMix) -> Insight | None:
    time_top = _dominant(sales.by_time)
    day_top = _dominant(sales.by_day)
    time_hit = time_top is not None and time_top[1] >= PEAK_TIME_MIN
    day_hit = day_top is not None and day_top[1] >= PEAK_DAY_MIN
    if time_hit and day_hit:
        text = (
            f"매출의 {round(time_top[1] * 100)}%가 {_TIME_LABELS[time_top[0]]}에 집중되고, "
            f"{_DAY_LABELS[day_top[0]]} 매출이 가장 큽니다."
        )
    elif time_hit:
        text = f"매출의 {round(time_top[1] * 100)}%가 {_TIME_LABELS[time_top[0]]}에 집중됩니다."
    elif day_hit:
        text = f"요일 중에는 {_DAY_LABELS[day_top[0]]} 매출이 {round(day_top[1] * 100)}%로 가장 큽니다."
    else:
        return None
    return Insight(key="sales_rhythm_peak", tone="neutral", text=text)


def _demand_insights(
    resident: ResidentProfile | None, working: WorkingProfile | None
) -> list[Insight]:
    out: list[Insight] = []
    if resident is not None and working is not None and resident.total > 0 and working.total > 0:
        ratio = working.total / resident.total
        if ratio >= OFFICE_RATIO:
            out.append(Insight(
                key="demand_type", tone="positive",
                text=f"직장인구 {_pop(working.total)}명이 상주인구의 {ratio:.1f}배 — "
                     "평일 점심·저녁 장사에 유리한 오피스 상권입니다.",
            ))
        elif ratio <= RESIDENT_RATIO:
            out.append(Insight(
                key="demand_type", tone="neutral",
                text=f"상주인구 {_pop(resident.total)}명이 직장인구의 {1 / ratio:.1f}배 — "
                     "저녁·주말 동네 수요 중심의 주거 상권입니다.",
            ))
        else:
            out.append(Insight(
                key="demand_type", tone="neutral",
                text=f"직장인구 {_pop(working.total)}명·상주인구 {_pop(resident.total)}명 — "
                     "주중·주말 수요가 섞인 혼합 상권입니다.",
            ))
    if resident is not None and resident.total_households > 0:
        share = resident.apartment_households / resident.total_households
        if share >= APT_SHARE_MIN:
            out.append(Insight(
                key="demand_apartment", tone="positive",
                text=f"배후 가구의 {round(share * 100)}%가 아파트 — 고정 주거 수요가 탄탄합니다.",
            ))
    return out


def _spending_insights(spending: SpendingProfile) -> list[Insight]:
    income = spending.monthly_avg_income
    top = spending.by_category[0] if spending.by_category else None
    if income and top:
        text = f"배후 주민 월평균 소득은 약 {_money(income)}, {top.label} 지출 비중이 가장 큽니다."
    elif income:
        text = f"배후 주민 월평균 소득은 약 {_money(income)}입니다."
    elif top:
        text = f"배후 주민 지출은 {top.label} 비중이 가장 큽니다."
    else:
        return []
    return [Insight(key="spending_power", tone="neutral", text=text)]


def _avg_ticket(sales: SalesMix) -> Insight | None:
    # 월 총매출 우선 — 성별 미상 매출이 빠진 성별 합은 폴백으로만 쓴다
    total = sales.monthly_amount if sales.monthly_amount > 0 else sum(sales.by_gender.values())
    if total <= 0 or sales.monthly_count <= 0:
        return None
    per = total / sales.monthly_count
    if per >= 10_000:
        fmt = f"{per / 10_000:.1f}만원"
    else:
        fmt = f"{per:,.0f}원"
    return Insight(
        key="avg_ticket", tone="neutral",
        text=f"건당 평균 결제액은 약 {fmt}입니다.",
    )


def _dominant(values: dict[str, int]) -> tuple[str, float] | None:
    """최댓값 키와 전체 대비 비중 — 합계 0이면 None."""
    total = sum(values.values())
    if total <= 0:
        return None
    key = max(values, key=values.get)  # type: ignore[arg-type]
    return key, values[key] / total


def _pop(n: int) -> str:
    return f"{n / 10_000:.1f}만" if n >= 10_000 else f"{n:,}"


def _money(won: float) -> str:
    if won >= 100_000_000:
        return f"{won / 100_000_000:.1f}억원"
    return f"{round(won / 10_000):,}만원"
