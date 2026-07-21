from fastapi import APIRouter, Depends

from admin.adapter.inbound.api.schemas.audit_schema import (
    AuditEntrySchema,
    AuditListResponseSchema,
)
from admin.app.dtos.audit_dto import AuditListQuery
from admin.app.ports.input.audit_use_case import AuditUseCase
from admin.dependencies.audit_provider import get_audit_use_case
from core.security import require_permission

audit_router = APIRouter(prefix="/admin", tags=["admin"])


@audit_router.get(
    "/audit",
    response_model=AuditListResponseSchema,
    dependencies=[Depends(require_permission("audit:read"))],
)
async def list_audit_logs(
    limit: int = 50,
    use_case: AuditUseCase = Depends(get_audit_use_case),
) -> AuditListResponseSchema:
    result = await use_case.list_logs(AuditListQuery(limit=limit))
    return AuditListResponseSchema(
        items=[
            AuditEntrySchema(
                id=e.id,
                actor_id=e.actor_id,
                action=e.action,
                detail=e.detail,
                created_at=e.created_at,
            )
            for e in result.items
        ]
    )
