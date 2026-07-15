from __future__ import annotations

from abc import ABC, abstractmethod


class SemanticRecordPort(ABC):
    """시멘틱 라우터 (hub/semantic)의 활동 기록 아웃바운드 포트. 구현(로그/DB)은 어댑터가 제공."""

    @abstractmethod
    async def record(self, subject: str, note: str) -> None: ...
