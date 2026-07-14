from __future__ import annotations

from abc import ABC, abstractmethod

from stock.domain.entities.fundamental_snapshot import FundamentalSnapshot


class FundamentalRepositoryPort(ABC):
    """펀더멘털 스냅샷 저장 아웃바운드 포트. 구현(PG 등)은 어댑터가 제공."""

    @abstractmethod
    async def save_many(self, snapshots: list[FundamentalSnapshot]) -> int:
        """저장하고 신규 건수를 반환한다. (ticker, as_of, source) 중복은 무시한다."""
        ...
