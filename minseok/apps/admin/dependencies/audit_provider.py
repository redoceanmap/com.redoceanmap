from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from admin.adapter.outbound.pg.audit_log_pg_adapter import AuditLogPgAdapter
from admin.app.ports.input.audit_use_case import AuditUseCase
from admin.app.ports.output.audit_log_port import AuditLogPort
from admin.app.use_cases.audit_interactor import AuditInteractor
from core.database import get_db


def get_audit_log_port(db: AsyncSession = Depends(get_db)) -> AuditLogPort:
    return AuditLogPgAdapter(session=db)


def get_audit_use_case(audit: AuditLogPort = Depends(get_audit_log_port)) -> AuditUseCase:
    return AuditInteractor(audit=audit)
