from fastapi import APIRouter, Depends, HTTPException

from admin.adapter.inbound.api.schemas.member_schema import (
    MemberListResponseSchema,
    MemberSchema,
    RoleGrantRequestSchema,
    RoleListResponseSchema,
    RoleSchema,
)
from admin.app.dtos.member_dto import MemberListQuery, RoleChangeCommand
from admin.app.ports.input.member_use_case import MemberUseCase
from admin.dependencies.member_provider import get_member_use_case
from core.security import require_permission
from hub.app.dtos.member_directory_dto import MemberInfo

member_router = APIRouter(prefix="/admin", tags=["admin"])


def _to_member_schema(m: MemberInfo) -> MemberSchema:
    return MemberSchema(
        id=m.id,
        email=m.email,
        name=m.name,
        joined_at=m.joined_at,
        marketing_agreed=m.marketing_agreed,
        roles=list(m.roles),
    )


@member_router.get(
    "/members",
    response_model=MemberListResponseSchema,
    dependencies=[Depends(require_permission("members:read"))],
)
async def list_members(
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
    use_case: MemberUseCase = Depends(get_member_use_case),
) -> MemberListResponseSchema:
    result = await use_case.list_members(MemberListQuery(search=search, limit=limit, offset=offset))
    return MemberListResponseSchema(
        total=result.page.total, items=[_to_member_schema(m) for m in result.page.items]
    )


@member_router.get(
    "/members/roles",
    response_model=RoleListResponseSchema,
    dependencies=[Depends(require_permission("members:read"))],
)
async def list_roles(
    use_case: MemberUseCase = Depends(get_member_use_case),
) -> RoleListResponseSchema:
    result = await use_case.list_roles()
    return RoleListResponseSchema(
        roles=[
            RoleSchema(code=r.code, name=r.name, permissions=list(r.permissions))
            for r in result.roles
        ]
    )


@member_router.post(
    "/members/{user_id}/roles",
    response_model=MemberSchema,
)
async def grant_role(
    user_id: int,
    body: RoleGrantRequestSchema,
    actor_id: int = Depends(require_permission("members:write")),
    use_case: MemberUseCase = Depends(get_member_use_case),
) -> MemberSchema:
    try:
        result = await use_case.grant_role(
            RoleChangeCommand(actor_id=actor_id, user_id=user_id, role_code=body.role_code)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _to_member_schema(result.member)


@member_router.delete(
    "/members/{user_id}/roles/{role_code}",
    response_model=MemberSchema,
)
async def revoke_role(
    user_id: int,
    role_code: str,
    actor_id: int = Depends(require_permission("members:write")),
    use_case: MemberUseCase = Depends(get_member_use_case),
) -> MemberSchema:
    try:
        result = await use_case.revoke_role(
            RoleChangeCommand(actor_id=actor_id, user_id=user_id, role_code=role_code)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _to_member_schema(result.member)
