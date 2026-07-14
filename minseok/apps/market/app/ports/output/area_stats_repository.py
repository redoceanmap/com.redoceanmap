from __future__ import annotations

from abc import ABC, abstractmethod

from market.app.dtos.area_stats_dto import (
    AreaHeader,
    ChangeSummary,
    FloatingQuarter,
    SalesQuarter,
    ServiceRef,
    StoreQuarter,
)


class AreaStatsRepositoryPort(ABC):
    """상권 통계 팩트 조회 아웃바운드 포트 — 시계열 병합은 인터랙터가 맡는다."""

    @abstractmethod
    async def find_header(self, trdar_code: int) -> AreaHeader | None:
        """상권명 + 자치구명. 상권이 없으면 None."""
        ...

    @abstractmethod
    async def resolve_service(self, trdar_code: int, service_code: str | None) -> ServiceRef | None:
        """업종 확정 — 지정 코드의 이름 조회, 미지정이면 최신 분기 매출 최대 업종."""
        ...

    @abstractmethod
    async def find_sales(
        self, trdar_code: int, service_code: str, quarters: int
    ) -> list[SalesQuarter]:
        """최근 quarters개 분기 매출 — year_quarter 오름차순."""
        ...

    @abstractmethod
    async def find_stores(
        self, trdar_code: int, service_code: str, quarters: int
    ) -> list[StoreQuarter]:
        """최근 quarters개 분기 점포 — year_quarter 오름차순."""
        ...

    @abstractmethod
    async def find_floating(self, trdar_code: int, quarters: int) -> list[FloatingQuarter]:
        """최근 quarters개 분기 유동인구(업종 무관) — year_quarter 오름차순."""
        ...

    @abstractmethod
    async def find_change(self, trdar_code: int) -> ChangeSummary | None:
        """최신 분기 상권변화지표 + 시도 벤치마크."""
        ...
