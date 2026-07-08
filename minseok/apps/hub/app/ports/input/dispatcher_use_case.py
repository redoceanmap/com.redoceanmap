from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.dispatcher_dto import DispatcherQuery, DispatcherResponse


class DispatcherUseCase(ABC):
    """자동화 창구 (hub/automation) 유스케이스 — 자동화 단일 창구(/automation/*)의 관제."""

    @abstractmethod
    async def introduce_myself(self, query: DispatcherQuery) -> DispatcherResponse:
        """자동화 창구 (hub/automation)의 자기소개 메소드."""
        ...
