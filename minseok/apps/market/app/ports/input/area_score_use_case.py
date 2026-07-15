from __future__ import annotations

from abc import ABC, abstractmethod

from market.app.dtos.area_score_dto import AreaScoreQuery, AreaScoreView


class AreaScoreUseCase(ABC):
    """상권 1곳의 분기 추이(QoQ) + 시도 벤치마크 대비 종합점수 조회."""

    @abstractmethod
    async def get_score(self, query: AreaScoreQuery) -> AreaScoreView | None:
        """상권이 없으면 None(HTTP 변환은 라우터 몫)."""
        ...
