from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.gemini_dto import (
    GeminiAnswerQuery,
    GeminiAnswerResponse,
    GeminiQuery,
    GeminiResponse,
)


class GeminiUseCase(ABC):
    """제미나이 답변기 (hub/gemini) 유스케이스 — 외부 Gemini API로 답변 생성."""

    @abstractmethod
    async def introduce_myself(self, query: GeminiQuery) -> GeminiResponse:
        """제미나이 답변기 (hub/gemini)의 자기소개 메소드."""
        ...

    @abstractmethod
    async def answer(self, query: GeminiAnswerQuery) -> GeminiAnswerResponse:
        """프롬프트를 Gemini API로 보내 답변 텍스트를 생성한다."""
        ...
