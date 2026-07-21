from __future__ import annotations

from pydantic import BaseModel


class SalesMixSchema(BaseModel):
    yearQuarter: int
    weekdayAmount: int
    weekendAmount: int
    byDay: dict[str, int]     # mon..sun
    byTime: dict[str, int]    # t00_06..t21_24
    byGender: dict[str, int]  # male, female
    byAge: dict[str, int]     # age10..age60Plus
    monthlyCount: int


class AgeBandSchema(BaseModel):
    band: str  # "10".."60+"
    male: int
    female: int


class PopulationSchema(BaseModel):
    yearQuarter: int
    total: int
    byAge: list[AgeBandSchema]


class HouseholdsSchema(BaseModel):
    total: int
    apartment: int


class ApartmentSchema(BaseModel):
    yearQuarter: int
    complexCount: int
    avgPrice: int  # 원
    avgArea: int   # ㎡


class DemandSchema(BaseModel):
    resident: PopulationSchema | None
    working: PopulationSchema | None
    households: HouseholdsSchema | None
    apartment: ApartmentSchema | None


class SpendingCategorySchema(BaseModel):
    key: str
    label: str
    amount: float  # 원


class SpendingSchema(BaseModel):
    yearQuarter: int
    monthlyAvgIncome: float | None
    totalExpenditure: float | None
    byCategory: list[SpendingCategorySchema]  # 금액 내림차순


class InsightSchema(BaseModel):
    key: str
    tone: str  # positive | neutral | warning
    text: str


class AreaDetailResponse(BaseModel):
    trdarCode: int
    trdarName: str
    districtName: str
    serviceCode: str | None  # 매출 팩트가 없는 상권이면 null
    serviceName: str | None
    salesMix: SalesMixSchema | None
    demand: DemandSchema | None
    spending: SpendingSchema | None
    insights: list[InsightSchema]
