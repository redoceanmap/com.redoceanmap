from __future__ import annotations

from abc import ABC, abstractmethod

from stock.domain.entities.fundamental_snapshot import FundamentalSnapshot


class FundamentalIngestUseCase(ABC):
    """수집 배치가 보낸 펀더멘털 스냅샷을 적재하는 인바운드 유스케이스."""

    @abstractmethod
    async def ingest(self, snapshots: list[FundamentalSnapshot]) -> int:
        """저장된 신규 건수를 반환한다."""
        ...
