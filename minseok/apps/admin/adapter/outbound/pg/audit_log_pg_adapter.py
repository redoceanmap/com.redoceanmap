from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin.adapter.outbound.orm.audit_log_orm import AuditLogOrm
from admin.app.dtos.audit_dto import AuditEntry
from admin.app.ports.output.audit_log_port import AuditLogPort


class AuditLogPgAdapter(AuditLogPort):
    """AuditLogPort의 PG 구현 — admin_audit_logs 테이블에 기록/조회."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def write(self, actor_id: int, action: str, detail: str) -> None:
        self._session.add(AuditLogOrm(actor_id=actor_id, action=action, detail=detail))
        await self._session.commit()

    async def list_recent(self, limit: int) -> list[AuditEntry]:
        rows = (
            await self._session.execute(
                select(AuditLogOrm).order_by(AuditLogOrm.id.desc()).limit(limit)
            )
        ).scalars().all()
        return [
            AuditEntry(
                id=r.id,
                actor_id=r.actor_id,
                action=r.action,
                detail=r.detail,
                created_at=r.created_at,
            )
            for r in rows
        ]
