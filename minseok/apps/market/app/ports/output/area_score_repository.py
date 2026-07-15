from __future__ import annotations

from abc import ABC, abstractmethod

from market.app.dtos.area_score_dto import (
    AreaScoreHeader,
    PersistenceStat,
    StoreHealthStat,
)
from market.domain.value_objects.area_score_vo import QuarterValue


class AreaScoreRepositoryPort(ABC):
    """상권 스코어링 입력 팩트 조회 아웃바운드 포트 — 계산은 도메인 스코어러가 맡는다."""

    @abstractmethod
    async def find_header(self, trdar_code: int) -> AreaScoreHeader | None:
        """상권명 + 자치구명 + 시도 코드. 상권이 없으면 None."""
        ...

    @abstractmethod
    async def find_sales_series(self, trdar_code: int, quarters: int) -> list[QuarterValue]:
        """최근 quarters개 분기의 전 업종 합계 매출 — year_quarter 오름차순."""
        ...

    @abstractmethod
    async def find_floating_series(self, trdar_code: int, quarters: int) -> list[QuarterValue]:
        """최근 quarters개 분기의 총 유동인구 — year_quarter 오름차순."""
        ...

    @abstractmethod
    async def find_city_sales_series(self, sido_code: str, quarters: int) -> list[QuarterValue]:
        """시도 전체의 분기별 합계 매출 — year_quarter 오름차순."""
        ...

    @abstractmethod
    async def find_city_floating_series(
        self, sido_code: str, quarters: int
    ) -> list[QuarterValue]:
        """시도 전체의 분기별 합계 유동인구 — year_quarter 오름차순."""
        ...

    @abstractmethod
    async def find_store_health(self, trdar_code: int) -> StoreHealthStat | None:
        """최신 분기의 업종 평균 개·폐업률. 점포 팩트가 없으면 None."""
        ...

    @abstractmethod
    async def find_city_store_health(
        self, sido_code: str, year_quarter: int
    ) -> StoreHealthStat | None:
        """지정 분기의 시도 전체 업종 평균 개·폐업률."""
        ...

    @abstractmethod
    async def find_persistence(
        self, trdar_code: int, sido_code: str | None
    ) -> PersistenceStat | None:
        """최신 분기 평균 영업 개월 + 같은 분기 시도 벤치마크."""
        ...
