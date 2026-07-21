from __future__ import annotations

from abc import ABC, abstractmethod


class DemandRecordPort(ABC):
    """분석 질문 수요 기록 아웃바운드 포트 — 실패해도 분석은 계속된다(베스트 에포트)."""

    @abstractmethod
    async def record(self, ticker: str) -> None:
        """ticker 질문 1회 기록 — upsert(ask_count+1, last_asked_at 갱신)."""
        ...
