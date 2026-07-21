from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.data_source_dto import DataSourceListResponse


class DataSourceUseCase(ABC):
    """어드민 데이터소스 유스케이스 — 데이터셋별 적재 현황."""

    @abstractmethod
    async def list_datasets(self) -> DataSourceListResponse:
        """market 데이터셋 + 추천 기록의 행수·최신 시점을 반환한다."""
        ...
