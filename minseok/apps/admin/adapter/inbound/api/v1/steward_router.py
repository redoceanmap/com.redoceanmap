from fastapi import APIRouter, Depends

from admin.adapter.inbound.api.schemas.steward_schema import (
    StewardAccessResponseSchema,
    StewardResponseSchema,
)
from admin.app.dtos.steward_dto import StewardAccessQuery, StewardQuery
from admin.app.ports.input.steward_use_case import StewardUseCase
from admin.dependencies.steward_provider import get_steward_use_case
from core.security import get_current_user_id

steward_router = APIRouter(prefix="/admin", tags=["admin"])


@steward_router.get("/myself", response_model=StewardResponseSchema)
async def introduce_myself(
    steward: StewardUseCase = Depends(get_steward_use_case),
) -> StewardResponseSchema:
    result = await steward.introduce_myself(StewardQuery(id=1, name="어드민 콘솔 (admin)"))
    return StewardResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )


@steward_router.get("/me", response_model=StewardAccessResponseSchema)
async def my_access(
    user_id: int = Depends(get_current_user_id),
    steward: StewardUseCase = Depends(get_steward_use_case),
) -> StewardAccessResponseSchema:
    """인증만 요구한다 — 비관리자는 빈 permissions(프론트 가드가 리다이렉트 판단)."""
    result = await steward.my_access(StewardAccessQuery(user_id=user_id))
    return StewardAccessResponseSchema(
        user_id=result.user_id, permissions=list(result.permissions)
    )
