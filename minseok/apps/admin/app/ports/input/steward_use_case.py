from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.steward_dto import (
    StewardAccessQuery,
    StewardAccessResponse,
    StewardQuery,
    StewardResponse,
)


class StewardUseCase(ABC):
    """어드민 콘솔 (admin) 유스케이스 — 운영 콘솔의 집사: 자기소개 + 접근 권한 판정."""

    @abstractmethod
    async def introduce_myself(self, query: StewardQuery) -> StewardResponse:
        """어드민 콘솔 (admin)의 자기소개 메소드."""
        ...

    @abstractmethod
    async def my_access(self, query: StewardAccessQuery) -> StewardAccessResponse:
        """호출자의 어드민 permission 코드 목록 — 프론트 /admin 가드 판정용."""
        ...
