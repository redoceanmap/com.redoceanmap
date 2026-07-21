from __future__ import annotations

from admin.app.dtos.member_dto import (
    MemberListQuery,
    MemberListResponse,
    RoleChangeCommand,
    RoleChangeResponse,
    RoleListResponse,
)
from admin.app.ports.input.member_use_case import MemberUseCase
from admin.app.ports.output.audit_log_port import AuditLogPort
from hub.app.ports.output.member_directory_port import MemberDirectoryPort

MAX_LIMIT = 100


class MemberInteractor(MemberUseCase):
    """어드민 회원 관리 대장 — 허브 MemberDirectoryPort에 위임하고 변경 행위를 감사 기록한다."""

    def __init__(self, members: MemberDirectoryPort, audit: AuditLogPort) -> None:
        self._members = members
        self._audit = audit

    async def list_members(self, query: MemberListQuery) -> MemberListResponse:
        limit = min(max(query.limit, 1), MAX_LIMIT)
        offset = max(query.offset, 0)
        page = await self._members.list_members(search=query.search, limit=limit, offset=offset)
        return MemberListResponse(page=page)

    async def list_roles(self) -> RoleListResponse:
        return RoleListResponse(roles=await self._members.list_roles())

    async def grant_role(self, command: RoleChangeCommand) -> RoleChangeResponse:
        member = await self._members.grant_role(command.user_id, command.role_code)
        await self._audit.write(
            actor_id=command.actor_id,
            action="role.grant",
            detail=f"user={command.user_id}({member.email}) role={command.role_code}",
        )
        return RoleChangeResponse(member=member)

    async def revoke_role(self, command: RoleChangeCommand) -> RoleChangeResponse:
        member = await self._members.revoke_role(command.user_id, command.role_code)
        await self._audit.write(
            actor_id=command.actor_id,
            action="role.revoke",
            detail=f"user={command.user_id}({member.email}) role={command.role_code}",
        )
        return RoleChangeResponse(member=member)
