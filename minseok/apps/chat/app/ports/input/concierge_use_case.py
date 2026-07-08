from __future__ import annotations

from abc import ABC, abstractmethod

from chat.app.dtos.concierge_dto import ConciergeQuery, ConciergeResponse


class ConciergeUseCase(ABC):
    """대화형 분석 창구 (chat) 유스케이스 — 대화 의도 분류(phase0)와 최종 서술의 창구."""

    @abstractmethod
    async def introduce_myself(self, query: ConciergeQuery) -> ConciergeResponse:
        """대화형 분석 창구 (chat)의 자기소개 메소드."""
        ...
