from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.fundamental_dto import FundamentalSnapshotItem


class FundamentalIngestUseCase(ABC):
    """수집 배치가 보낸 펀더멘털 스냅샷을 받아들이는 허브 인바운드 유스케이스."""

    @abstractmethod
    async def ingest(self, items: list[FundamentalSnapshotItem]) -> int:
        """저장된 신규 건수를 반환한다."""
        ...
