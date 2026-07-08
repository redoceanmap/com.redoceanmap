from __future__ import annotations

from abc import ABC, abstractmethod

from recommendation.app.dtos.curator_dto import CuratorQuery, CuratorResponse


class CuratorUseCase(ABC):
    """추천 기록 (recommendation) 유스케이스 — 추천 이력의 보관과 재조회."""

    @abstractmethod
    async def introduce_myself(self, query: CuratorQuery) -> CuratorResponse:
        """추천 기록 (recommendation)의 자기소개 메소드."""
        ...
