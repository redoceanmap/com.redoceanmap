from __future__ import annotations

from abc import ABC, abstractmethod

from stock.app.dtos.forecast_snapshot_dto import SnapshotScoreUpdate
from stock.domain.entities.forecast_snapshot import ForecastSnapshot


class ForecastSnapshotRepositoryPort(ABC):
    """예측 스냅샷 영속 아웃바운드 포트."""

    @abstractmethod
    async def save_many(self, snapshots: list[ForecastSnapshot]) -> int:
        """저장하고 신규 건수를 반환한다. (ticker, horizon_days, as_of) 중복은 무시."""
        ...

    @abstractmethod
    async def find_pending(self) -> list[ForecastSnapshot]:
        """미채점(evaluated_at IS NULL) 스냅샷 전부 — 채점 배치 입력."""
        ...

    @abstractmethod
    async def apply_scores(self, updates: list[SnapshotScoreUpdate]) -> int:
        """채점 결과를 반영하고 반영 건수를 반환한다."""
        ...

    @abstractmethod
    async def find_scored(self, horizon: int | None, limit: int) -> list[ForecastSnapshot]:
        """채점 완료분(evaluated_at 내림차순) — 요약 집계 재료."""
        ...

    @abstractmethod
    async def find_recent(self, horizon: int | None, limit: int) -> list[ForecastSnapshot]:
        """최근 스냅샷(as_of 내림차순) — 어드민 목록."""
        ...

    @abstractmethod
    async def counts(self, horizon: int | None) -> tuple[int, int]:
        """(전체, 채점 완료) 건수."""
        ...
