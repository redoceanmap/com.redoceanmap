from __future__ import annotations

from abc import ABC, abstractmethod

from auth.app.dtos.gatekeeper_dto import GatekeeperQuery, GatekeeperResponse


class GatekeeperUseCase(ABC):
    """인증 서비스 (auth) 유스케이스 — 인증/인가의 관문 — 로그인·토큰 검증."""

    @abstractmethod
    async def introduce_myself(self, query: GatekeeperQuery) -> GatekeeperResponse:
        """인증 서비스 (auth)의 자기소개 메소드."""
        ...
