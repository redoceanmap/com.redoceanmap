from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.recommendation_directory_dto import RecommendationInfo, RecommendationStats


class RecommendationDirectoryPort(ABC):
    """허브가 스포크에 위임하는 추천 기록 열람 추상.

    기존 RecommendationRecordPort(기록·쓰기)와 별개인 조회 전용 계약.
    구현은 recommendation(스포크)이 제공하고, 합성 루트(main.py)에서 주입한다.
    """

    @abstractmethod
    async def list_recent(self, limit: int) -> list[RecommendationInfo]:
        """최근 추천 기록을 최신순으로 반환한다."""
        ...

    @abstractmethod
    async def stats(self) -> RecommendationStats:
        """총계·오늘 건수·최근 12개월 추이·상위 업종 분포를 반환한다."""
        ...
