from __future__ import annotations

from abc import ABC, abstractmethod

from mail.app.dtos.judge_dto import JudgeQuery, JudgeResponse


class JudgeUseCase(ABC):
    """저지(핵심 추론·판단) 유스케이스 — 배역: [[mail-agent-casting]]의 detective_holmes_judge."""

    @abstractmethod
    async def introduce_myself(self, query: JudgeQuery) -> JudgeResponse:
        """저지의 자기소개 메소드."""
        ...
