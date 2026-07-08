from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.recommendation_record_dto import RecommendedArea


class RecommendationRecordPort(ABC):
    """허브가 스포크에 위임하는 추천 기록 추상.

    허브는 이 포트(추상)만 알고 어떤 스포크가 구현하는지 모른다(스타 토폴로지 허브 격리).
    구현은 스포크(recommendation)가 제공하고, 합성 루트(main.py)에서 주입한다.
    """

    @abstractmethod
    async def record(
        self, conversation_id: int | None, areas: list[RecommendedArea]
    ) -> None:
        """대화가 만든 추천 묶음을 영속화한다(부작용, 반환값 없음)."""
        ...
