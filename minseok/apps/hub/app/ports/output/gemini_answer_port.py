from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.gemini_dto import GeminiAnswerResponse


class GeminiAnswerError(Exception):
    """Gemini 답변 생성 실패(키 미설정·HTTP 오류·빈 응답) — 계약 예외."""


class GeminiAnswerPort(ABC):
    """Gemini API 호출 아웃바운드 포트. 구현(REST 어댑터)은 어댑터가 제공."""

    @abstractmethod
    async def generate(self, prompt: str) -> GeminiAnswerResponse:
        """프롬프트로 답변을 생성한다. 실패는 GeminiAnswerError로 알린다."""
        ...
