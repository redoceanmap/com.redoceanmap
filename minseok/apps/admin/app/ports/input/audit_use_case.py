from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.audit_dto import AuditListQuery, AuditListResponse


class AuditUseCase(ABC):
    """어드민 감사 로그 유스케이스 — 관리자 행위 기록 열람."""

    @abstractmethod
    async def list_logs(self, query: AuditListQuery) -> AuditListResponse:
        """최근 감사 기록을 최신순으로 반환한다."""
        ...
