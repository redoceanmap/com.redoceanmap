from __future__ import annotations

from abc import ABC, abstractmethod


class PostmasterRecordPort(ABC):
    """이메일 발송 창구 (hub/email)의 활동 기록 아웃바운드 포트. 구현(로그/DB)은 어댑터가 제공."""

    @abstractmethod
    async def record(self, subject: str, note: str) -> None: ...
