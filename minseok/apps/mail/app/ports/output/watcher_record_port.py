from __future__ import annotations

from abc import ABC, abstractmethod


class WatcherRecordPort(ABC):
    """왓처(기록자)가 관찰 내용을 남기는 아웃바운드 포트.

    트리아지 구현 시 분류 결과(일반/격상 판정) 기록이 이 포트로 나간다.
    구현(로그/DB 등)은 어댑터가 제공.
    """

    @abstractmethod
    async def record(self, subject: str, note: str) -> None: ...
