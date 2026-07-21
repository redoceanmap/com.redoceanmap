from __future__ import annotations

from admin.app.dtos.audit_dto import AuditListQuery, AuditListResponse
from admin.app.ports.input.audit_use_case import AuditUseCase
from admin.app.ports.output.audit_log_port import AuditLogPort

MAX_LIMIT = 200


class AuditInteractor(AuditUseCase):
    """어드민 감사 로그 대장 — AuditLogPort에 위임한다."""

    def __init__(self, audit: AuditLogPort) -> None:
        self._audit = audit

    async def list_logs(self, query: AuditListQuery) -> AuditListResponse:
        limit = min(max(query.limit, 1), MAX_LIMIT)
        return AuditListResponse(items=await self._audit.list_recent(limit))
